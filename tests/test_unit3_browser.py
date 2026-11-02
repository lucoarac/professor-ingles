from pathlib import Path
import os
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
html=(root/'index.html').read_text()
for name in ['src/evaluator.js','src/persistence.js','src/unit2.js','src/unit3.js','src/unit4.js']:
    html=html.replace(f'<script src="{name}"></script>', '<script>'+(root/name).read_text()+'</script>')
checks=[]
def verify(name,ok):
    checks.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+name)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or p.chromium.executable_path,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html)
    page.locator('#unit3').click()
    verify('Aula 3 abre',page.locator('#english').inner_text()=='Do you work here?')
    for _ in range(4):page.locator('#next').click()
    verify('Aula 3 quinto cartão',page.locator('#english').inner_text()=='What are you going to do tomorrow?')
    page.locator('#next').click()
    verify('Aula 3 cinco perguntas',page.locator('#questions .question').count()==5)
    page.locator('#q0').fill('Do you work here?')
    page.locator('input[name="q1"][value="1"]').check()
    page.locator('#q2').fill("He isn't at home.")
    page.locator('input[name="q3"][value="2"]').check()
    page.locator('#q4').fill('What are you going to do tomorrow?')
    page.locator('#grade').click()
    verify('Aula 3 respostas previstas 5/5','5/5' in page.locator('#results').inner_text())
    verify('Aula 3 sem exceção JS',not errors)
    browser.close()
print('RESULT',sum(checks),'/',len(checks))
assert all(checks)
