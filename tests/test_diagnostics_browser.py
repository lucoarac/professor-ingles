"""DOM behavior checks for the diagnostics page; browser APIs are explicit test doubles."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'diagnostics.html').read_text(encoding='utf-8')
checks=[]
def verify(name, condition):
    checks.append(bool(condition))
    print(('PASS ' if condition else 'FAIL ')+name)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=__import__('os').environ.get('CHROMIUM_PATH') or p.chromium.executable_path, args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page()
    page_errors=[]
    page.on('pageerror', lambda error: page_errors.append(str(error)))
    page.goto("about:blank")
    page.evaluate("""
      const makeStore=()=>{const data={};return {getItem:k=>Object.prototype.hasOwnProperty.call(data,k)?data[k]:null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k]}};
      Object.defineProperty(window,'localStorage',{configurable:true,value:makeStore()});
      Object.defineProperty(window,'sessionStorage',{configurable:true,value:makeStore()});
      Object.defineProperty(window,'isSecureContext',{configurable:true,value:true});
      window.__micRequests=0;window.__asrStarts=0;window.__tracksStopped=0;
      Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:async()=>{window.__micRequests++;return {getTracks:()=>[{stop:()=>window.__tracksStopped++}]}}}});
      window.MediaRecorder=class {static isTypeSupported(){return false} constructor(){this.state='inactive';this.mimeType='audio/webm'} start(){this.state='recording'} stop(){this.state='inactive';this.ondataavailable?.({data:new Blob(['fake-audio'])});this.onstop?.()}};
      window.SpeechRecognition=class {start(){window.__asrStarts++}abort(){}};
      window.speechSynthesis={getVoices:()=>[],cancel(){},speak(u){u.onend?.()},addEventListener(){}};
      window.SpeechSynthesisUtterance=class {constructor(text){this.text=text}};
      window.confirm=()=>true;
      const nativeTimeout=window.setTimeout.bind(window);window.setTimeout=(fn,ms,...args)=>nativeTimeout(fn,ms===2000?0:ms,...args);
    """)
    page.set_content(HTML,wait_until='load')
    verify('Página inicializa sem exceção JS', page.locator('h1').inner_text().startswith('Diagnóstico'))
    verify('Microfone não é solicitado automaticamente', page.evaluate('window.__micRequests===0'))
    verify('Reconhecimento não inicia automaticamente', page.evaluate('window.__asrStarts===0'))
    verify('Relatório inicial contém capacidades', 'speechRecognition' in page.locator('#apiSummary').inner_text())
    page.locator('#recognizeTest').click()
    verify('Reconhecimento só inicia após clique e consentimento', page.evaluate('window.__asrStarts===1'))
    page.locator('#recordTest').click()
    page.wait_for_timeout(100)
    verify('Microfone só é solicitado após clique', page.evaluate('window.__micRequests===1'))
    verify('Tracks são encerradas após gravação simulada', page.evaluate('window.__tracksStopped===1'))
    verify('Player de gravação é exibido após captura simulada', not page.locator('#playback').evaluate("e=>e.classList.contains('hidden')"))
    verify('Sem exceções JavaScript na página de diagnóstico', not page_errors)
    browser.close()
print(f'RESULT {sum(checks)}/{len(checks)}')
assert all(checks)
