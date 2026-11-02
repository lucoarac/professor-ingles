"""Actual localhost HTTP integration: persistence survives a full browser reload."""
from pathlib import Path
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
from playwright._impl._errors import Error as PlaywrightError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
url = f'http://127.0.0.1:{server.server_address[1]}/index.html'
checks = []

def verify(name, condition):
    checks.append(bool(condition))
    print(('PASS ' if condition else 'FAIL ') + name)

try:
    # Confirm the server itself serves the app before attempting Chromium navigation.
    with urlopen(url, timeout=3) as http_response:
        print(('PASS ' if http_response.status == 200 else 'FAIL ') + 'HTTP server serves index.html')
        checks.append(http_response.status == 200)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or p.chromium.executable_path, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 390, 'height': 844})
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        try:
            response = page.goto(url, wait_until='networkidle')
        except PlaywrightError as error:
            if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(error):
                print('BLOCKED Chromium localhost navigation by execution-environment policy; native browser reload NOT_RUN')
                raise SystemExit(77)
            raise
        verify('Aplicação servida por HTTP localhost (200)', response is not None and response.status == 200)
        verify('Aplicação inicia na primeira aula', page.locator('#count').inner_text() == 'Cartão 1/5')

        # Navigate to unit 3, card 3; then perform a genuine reload on the same origin.
        page.locator('#unit3').click()
        page.locator('#next').click()
        page.locator('#next').click()
        verify('Posição da aula 3/cartão 3 foi persistida', page.evaluate("JSON.parse(localStorage.getItem('english-professor-state-v1')).position") == {'unit': 2, 'card': 2})
        page.reload(wait_until='networkidle')
        verify('Recarga HTTP restaura unidade 3 e cartão 3', page.locator('#courseStatus').inner_text().startswith('A1 · Aula 3') and page.locator('#count').inner_text() == 'Cartão 3/5')

        # Complete unit 3 using accepted variants, checking aggregate-only persistence.
        page.locator('#next').click()
        page.locator('#next').click()
        page.locator('#next').click()
        verify('Questionário da aula 3 abre', page.locator('#quizPage').is_visible())
        page.locator('#q0').fill('Do you work here?')
        page.locator('input[name="q1"][value="1"]').check()
        page.locator('#q2').fill("He's not at home.")
        page.locator('input[name="q3"][value="2"]').check()
        page.locator('#q4').fill('What are you going to do tomorrow?')
        page.locator('#grade').click()
        verify('Aula 3 conclui avaliação 5/5', '5/5' in page.locator('#results').inner_text())
        verify('Contador de conclusão é atualizado', '1/4 aulas concluídas' in page.locator('#localProgress').inner_text())
        stored = page.evaluate("localStorage.getItem('english-professor-state-v1')")
        verify('Persistência não armazena texto das respostas', 'Do you work here?' not in stored and "He's not at home." not in stored)

        page.reload(wait_until='networkidle')
        verify('Conclusão 1/4 sobrevive à recarga HTTP', '1/4 aulas concluídas' in page.locator('#localProgress').inner_text())
        verify('Posição da última aula continua restaurada', page.locator('#courseStatus').inner_text().startswith('A1 · Aula 3'))

        # User-confirmed reset removes current state and legacy keys.
        page.on('dialog', lambda dialog: dialog.accept())
        page.locator('#clear').click()
        verify('Reset apaga conclusão e reinicia aula 1', '0/4 aulas concluídas' in page.locator('#localProgress').inner_text() and page.locator('#count').inner_text() == 'Cartão 1/5')
        page.reload(wait_until='networkidle')
        verify('Reset também persiste após recarga', '0/4 aulas concluídas' in page.locator('#localProgress').inner_text() and page.locator('#count').inner_text() == 'Cartão 1/5')
        verify('Sem exceções JavaScript no fluxo HTTP', not errors)
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)

print(f'RESULT {sum(checks)}/{len(checks)}')
assert all(checks)
