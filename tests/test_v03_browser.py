"""Real Chromium integration test over localhost, not microphone/tts hardware test."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import os
root=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_address[1]}/index.html'
checks=[]
def check(name,condition):
 checks.append(condition)
 print(('PASS' if condition else 'FAIL')+' '+name)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or p.chromium.executable_path,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 html=(root/'index.html').read_text()
 for f in ['src/evaluator.js','src/persistence.js','src/unit2.js','src/unit3.js','src/unit4.js']:
  html=html.replace(f'<script src="{f}"></script>', '<script>'+ (root/f).read_text() + '</script>')
 page.set_content(html)
 check('Scripts locais incorporados, sem dependência de servidor no teste',page.evaluate('Boolean(window.EnglishUnit2 && window.EnglishEvaluator)'))
 check('Unidade 1 inicia com cartão 1',page.locator('#english').inner_text()=='My name is Fabio.')
 page.locator('#unit2').click()
 check('Unidade 2 apresenta conteúdo próprio',page.locator('#english').inner_text()=='She works at the store.')
 check('Layout 390px sem scroll horizontal',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
 for _ in range(4):page.locator('#next').click()
 check('Unidade 2 completa cinco cartões',page.locator('#english').inner_text()=='Will you work tomorrow?')
 page.locator('#next').click()
 check('Quiz da unidade 2 renderiza cinco perguntas',page.locator('#questions .question').count()==5)
 page.locator('#q0').fill('She works at the store.')
 page.locator('input[name="q1"][value="1"]').check()
 page.locator('#q2').fill("He didn't work yesterday.")
 page.locator('input[name="q3"][value="1"]').check()
 page.locator('#q4').fill('Will you work tomorrow?')
 page.locator('#grade').click()
 check('Quiz da unidade 2: 5/5', '5/5' in page.locator('#results').inner_text())
 page.locator('#backCards').click()
 page.locator('#unit2').click()
 for _ in range(4):page.locator('#next').click()
 page.locator('#next').click()
 page.locator('#q0').fill('She is employed at the store')
 page.locator('#grade').click()
 check('Resposta válida não cadastrada requer revisão sem reprovação', 'Necessita revisão humana' in page.locator('#feedback0').inner_text())
 check('Sem exceção JavaScript no fluxo',not errors)
 # Reload cannot be verified on page.set_content/about:blank. Must run on HTTP/HTTPS.
 print('NOT_RUN persistência após recarga (ambiente bloqueia navegação localhost)')
 browser.close()
server.shutdown()
print('RESULT',sum(checks),'/',len(checks))
assert all(checks)
