from pathlib import Path
import os
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
html=(root/'index.html').read_text()
for name in ['src/evaluator.js','src/persistence.js','src/unit2.js','src/unit3.js','src/unit4.js']:
    html=html.replace(f'<script src="{name}"></script>', '<script>'+(root/name).read_text()+'</script>')
checks=[]
def verify(n,ok):
    checks.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+n)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or p.chromium.executable_path,args=['--no-sandbox'])
    page=b.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html)
    page.locator('#unit4').click()
    verify('Aula 4 inicia',page.locator('#english').inner_text()=='I study English every day.')
    for _ in range(4):page.locator('#next').click()
    verify('Cinco cartões Aula 4',page.locator('#english').inner_text()=='I will study English tomorrow.')
    page.locator('#next').click()
    verify('Cinco questões Aula 4',page.locator('#questions .question').count()==5)
    page.locator('#q0').fill('I study English every day.')
    page.locator('input[name="q1"][value="1"]').check()
    page.locator('input[name="q2"][value="2"]').check()
    page.locator('#q3').fill('I was studying at eight.')
    page.locator('#q4').fill('I will study tomorrow.')
    page.locator('#grade').click()
    verify('Aula 4 avaliação 5/5','5/5' in page.locator('#results').inner_text())
    verify('Sem erros JavaScript',not errors)
    verify('Layout mobile sem overflow',page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'))
    b.close()
print('RESULT',sum(checks),'/',len(checks))
assert all(checks)
