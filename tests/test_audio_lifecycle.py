"""Mocked API lifecycle tests; do not represent physical microphone or cloud ASR validation."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'index.html').read_text()
for name in ['src/evaluator.js', 'src/persistence.js', 'src/unit2.js', 'src/unit3.js', 'src/unit4.js']:
    html = html.replace(f'<script src="{name}"></script>', '<script>' + (ROOT / name).read_text() + '</script>')
checks = []
def verify(name, condition):
    checks.append(bool(condition)); print(('PASS ' if condition else 'FAIL ') + name)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or p.chromium.executable_path, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    page.set_content(html)
    page.evaluate("""() => {
      window.__micStops=0; window.__micResolve=null; window.__asrStarts=0; window.__asrAborts=0; window.__asrInstances=[];
      Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:()=>new Promise(resolve=>window.__micResolve=resolve)}});
      window.MediaRecorder=class {constructor(){this.state='inactive';this.mimeType='audio/webm'}start(){this.state='recording'}stop(){this.state='inactive';if(this.onstop)this.onstop()}};
      window.SpeechRecognition=class {constructor(){this.lang='';window.__asrInstances.push(this)}start(){window.__asrStarts++}abort(){window.__asrAborts++}};
      window.confirm=()=>true;
    }""")
    page.locator('#record').click()
    page.locator('#next').click()
    page.evaluate("window.__micResolve({getTracks:()=>[{stop:()=>window.__micStops++}]})")
    verify('Permissão tardia do microfone é descartada após trocar cartão', page.evaluate('window.__micStops') == 1 and 'Gravar minha repetição' in page.locator('#record').inner_text())

    page.locator('#recognize').click()
    verify('Consentimento aceito inicia reconhecimento simulado', page.evaluate('window.__asrStarts') == 1)
    old_result = page.evaluate("""() => { const r=window.__asrInstances[0]; return typeof r.onresult === 'function' }""")
    page.locator('#next').click()
    verify('Navegação aborta reconhecimento em andamento', page.evaluate('window.__asrAborts') == 1)
    page.evaluate("""() => { const r=window.__asrInstances[0]; if(r.onresult)r.onresult({results:[[{transcript:'stale answer'}]]}) }""")
    verify('Resultado tardio não altera o cartão novo', 'Transcrição estimada' not in page.locator('#speechStatus').inner_text())
    verify('Instância ASR foi criada para teste de corrida', bool(old_result))

    # A user can decline the explicit disclosure; no recognizer should start.
    page.evaluate('window.confirm=()=>false; recognitionConsent=false')
    page.locator('#recognize').click()
    verify('Recusa de consentimento não inicia reconhecimento', page.evaluate('window.__asrStarts') == 1)

    page.evaluate("Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:async()=>{throw new DOMException('denied','NotAllowedError')}}})")
    page.locator('#record').click()
    page.wait_for_function("document.querySelector('#speechStatus').textContent.includes('permissão negada')")
    verify('Permissão de microfone negada gera mensagem específica', 'permissão negada' in page.locator('#speechStatus').inner_text())

    page.evaluate("""() => { window.__cleanup=0; Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:async()=>({getTracks:()=>[{stop:()=>window.__cleanup++}]})}}); window.MediaRecorder=class MockMediaRecorder { constructor(){throw new DOMException('unsupported','NotSupportedError')} }; }""")
    page.locator('#record').click()
    page.wait_for_function("window.__cleanup===1")
    verify('Falha ao criar MediaRecorder libera a stream obtida', page.evaluate('window.__cleanup') == 1)
    browser.close()

print(f'RESULT {sum(checks)}/{len(checks)}')
assert all(checks)
