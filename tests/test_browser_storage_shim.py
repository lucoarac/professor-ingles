"""App-level storage-contract integration test; NOT native HTTP/localStorage proof."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'index.html').read_text()
for name in ['src/evaluator.js', 'src/persistence.js', 'src/unit2.js', 'src/unit3.js', 'src/unit4.js']:
    html = html.replace(f'<script src="{name}"></script>', '<script>' + (ROOT / name).read_text() + '</script>')
shim = '''<script>(() => {
function read(){try{const x=JSON.parse(window.name||'{}');return x.__testLocalStorage||{}}catch{return {}}}
const api={getItem(k){const d=read();return Object.prototype.hasOwnProperty.call(d,k)?d[k]:null},setItem(k,v){const d=read();d[String(k)]=String(v);window.name=JSON.stringify({__testLocalStorage:d})},removeItem(k){const d=read();delete d[String(k)];window.name=JSON.stringify({__testLocalStorage:d})}};
Object.defineProperty(window,'localStorage',{configurable:true,value:api});
})();</script>'''
html = html.replace('</head>', shim + '</head>')
checks = []
def verify(name, condition):
    checks.append(bool(condition)); print(('PASS ' if condition else 'FAIL ') + name)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or p.chromium.executable_path, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(html)
    initial = page.evaluate("JSON.parse(localStorage.getItem('english-professor-state-v1'))")
    verify('Primeira inicialização grava estado vazio versionado', initial['version'] == 1 and initial['position'] == {'unit': 0, 'card': 0})
    page.locator('#unit4').click()
    page.locator('#next').click()
    page.locator('#next').click()
    saved = page.evaluate("JSON.parse(localStorage.getItem('english-professor-state-v1'))")
    verify('App grava a posição através do contrato Storage', saved['position'] == {'unit': 3, 'card': 2})
    restored = page.evaluate("EnglishPersistence.load(localStorage,[5,5,5,5])")
    verify('Módulo consegue ler de volta posição gravada', restored['state']['position'] == {'unit': 3, 'card': 2})
    page.locator('#next').click()
    page.locator('#next').click()
    page.locator('#next').click()
    page.locator('#q0').fill('I study English daily.')
    page.locator('input[name="q1"][value="1"]').check()
    page.locator('input[name="q2"][value="2"]').check()
    page.locator('#q3').fill('I was studying at 8 o’clock.')
    page.locator('#q4').fill("I'll study tomorrow.")
    page.locator('#grade').click()
    verify('Resultado agregado é persistido após avaliação', '1/4 aulas concluídas' in page.locator('#localProgress').inner_text())
    persisted = page.evaluate("JSON.parse(localStorage.getItem('english-professor-state-v1'))")
    verify('Estado salvo contém apenas resumo, sem respostas livres', 'I study English daily' not in str(persisted) and persisted['completedUnits']['3']['correct'] == 5)
    page.evaluate('window.confirm=()=>true')
    page.locator('#clear').click()
    cleared = page.evaluate("JSON.parse(localStorage.getItem('english-professor-state-v1'))")
    verify('Reset da interface elimina resultados e volta à primeira posição', cleared['completedUnits'] == {} and cleared['position'] == {'unit': 0, 'card': 0})
    verify('Sem exceções JavaScript', not errors)
    browser.close()

print(f'RESULT {sum(checks)}/{len(checks)}')
assert all(checks)
