"""Accessibility smoke checks for labels, status, focus and selected contrast pairs; not WCAG certification."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'index.html').read_text()
for name in ['src/evaluator.js', 'src/persistence.js', 'src/unit2.js', 'src/unit3.js', 'src/unit4.js']:
    html = html.replace(f'<script src="{name}"></script>', '<script>' + (ROOT / name).read_text() + '</script>')
checks=[]
def verify(name, condition):
    checks.append(bool(condition)); print(('PASS ' if condition else 'FAIL ') + name)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or p.chromium.executable_path,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844})
    page.set_content(html)
    bar=page.locator('#progress')
    verify('Progresso tem papel e valores acessíveis', bar.get_attribute('role')=='progressbar' and bar.get_attribute('aria-valuemin')=='1' and bar.get_attribute('aria-valuenow')=='1')
    verify('Frase inglesa declara idioma para leitores de tela', page.locator('#english').get_attribute('lang')=='en')
    verify('Status local é anunciado como status', page.locator('#localProgress').get_attribute('role')=='status')
    verify('Botão de gravação expõe estado inicial', page.locator('#record').get_attribute('aria-pressed')=='false')
    page.locator('#next').click()
    verify('Progresso atualiza valor acessível', bar.get_attribute('aria-valuenow')=='2' and 'Cartão 2 de 5'==bar.get_attribute('aria-valuetext'))
    verify('Foco vai para a frase ao trocar cartão', page.evaluate("document.activeElement.id")=='english')
    for _ in range(3): page.locator('#next').click()
    page.locator('#next').click()
    verify('Entrada de escrita tem nome acessível', bool(page.locator('#q0').get_attribute('aria-label')))
    verify('Entrada e opções de resposta declaram inglês', page.locator('#q0').get_attribute('lang')=='en' and page.locator('#questions label').first.get_attribute('lang')=='en')
    verify('Foco vai ao título da avaliação', page.evaluate("document.activeElement.id")=='quizTitle')
    verify('CSS declara indicador de foco visível', ':focus-visible' in html)
    contrast=page.evaluate("""() => {
      const rgb = s => s.match(/[\\d.]+/g).map(Number).slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4});
      const lum = c => .2126*c[0]+.7152*c[1]+.0722*c[2];
      const ratio = (a,b)=>{a=lum(rgb(a));b=lum(rgb(b));return (Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
      return {muted:ratio(getComputedStyle(document.querySelector('.muted')).color,'rgb(255, 255, 255)'), primary:ratio(getComputedStyle(document.querySelector('.primary')).color,getComputedStyle(document.querySelector('.primary')).backgroundColor)};
    }""")
    verify('Contraste calculado em dois pares usuais é >= 4.5', contrast['muted']>=4.5 and contrast['primary']>=4.5)
    browser.close()
print(f'RESULT {sum(checks)}/{len(checks)}')
assert all(checks)
