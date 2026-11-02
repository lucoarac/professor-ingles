"""Extra deterministic checks, no claims about real microphone or speech quality."""
import re,time,statistics,os
from pathlib import Path
from playwright.sync_api import sync_playwright
html=(Path(__file__).parents[1]/'index.html').read_text()
checks=[]
def verify(label,condition):
 checks.append((label,bool(condition)))
 print(('PASS' if condition else 'FAIL'),label)
verify('UNIT: document language is pt-BR','lang="pt-BR"' in html)
verify('UNIT: scripts use strict',"'use strict'" in html)
verify('UNIT: no external scripts',all(x in ['src/evaluator.js','src/persistence.js','src/unit2.js','src/unit3.js','src/unit4.js'] for x in re.findall(r'<script[^>]+src="([^"]+)"',html)))
verify('UNIT: no hardcoded remote API credentials',not re.search(r'\b(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{16,})\b',html))
verify('UNIT: recordings not uploaded via fetch',not re.search(r'\b(fetch|XMLHttpRequest)\s*\(',html))
verify('UNIT: repeated card invalidates audio/recording','function invalidateSession()' in html and 'stopRecording()' in html)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or pw.chromium.executable_path,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 
 for f in ['src/evaluator.js','src/persistence.js','src/unit2.js','src/unit3.js','src/unit4.js']:
  html=html.replace(f'<script src="{f}"></script>', '<script>'+(Path(__file__).parents[1]/f).read_text()+'</script>')
 page.set_content(html)
 # Real UI with fake device API: behavioral interaction, NOT physical audio
 page.evaluate('''() => {
  window.__stops=0;
  Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:async()=>({getTracks:()=>[{stop:()=>window.__stops++}]})}});
  window.MediaRecorder=class { constructor(stream){this.stream=stream;this.state='inactive';this.mimeType='audio/webm'} start(){this.state='recording'} stop(){this.state='inactive';if(this.ondataavailable)this.ondataavailable({data:new Blob(['test'])});if(this.onstop)this.onstop()} };
 }''')
 page.locator('#record').click()
 verify('INT: recording button enters active state','Encerrar gravação' in page.locator('#record').inner_text())
 page.locator('#next').click()
 verify('REG: leaving card stops recording',page.evaluate('window.__stops')>=1)
 verify('REG: record action resets after navigation','Gravar minha repetição' in page.locator('#record').inner_text())
 # measure 30 card changes, under headless injected DOM (not representative network/physical device)
 durations=[]
 for i in range(30):
  start=time.perf_counter()
  if page.locator('#prev').is_enabled():page.locator('#prev').click()
  else:page.locator('#next').click()
  durations.append((time.perf_counter()-start)*1000)
 print('MEASURE UI click+DOM median_ms=',round(statistics.median(durations),2),'p95_ms=',round(sorted(durations)[int(len(durations)*0.95)-1],2),'samples=',len(durations))
 browser.close()
print('TOTAL',sum(ok for _,ok in checks),'/',len(checks))
raise SystemExit(0 if all(x for _,x in checks) else 1)
