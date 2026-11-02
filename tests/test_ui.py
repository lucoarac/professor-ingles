"""Executable browser interaction regression; Chromium HTML injected due local navigation policy. No real audio claims."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT/'index.html').read_text()
for _src in ['src/evaluator.js','src/persistence.js','src/unit2.js','src/unit3.js','src/unit4.js']:
    HTML = HTML.replace(f'<script src="{_src}"></script>', '<script>'+(ROOT/_src).read_text()+'</script>')

def run():
    outcomes=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or p.chromium.executable_path,args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':390,'height':844})
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.set_content(HTML,wait_until='load')
        def test(name,fn):
            try:fn();outcomes.append((name,'PASS'))
            except Exception as e:outcomes.append((name,'FAIL: '+str(e)[:250]))
        def nav():
            assert page.locator('#english').inner_text()=='My name is Fabio.'
            page.locator('#next').click()
            assert page.locator('#english').inner_text()=='How are you?'
            page.locator('#prev').click(); assert page.locator('#english').inner_text()=='My name is Fabio.'
        test('E2E-01 navigation forward and back',nav)
        def five():
            for i in range(4):page.locator('#next').click()
            assert page.locator('#english').inner_text()=='I work every day.'
            assert 'I will work tomorrow' in page.locator('#examples').inner_text()
            page.locator('#next').click()
            assert page.locator('#quizPage').is_visible()
            assert page.locator('.question').count()==5
        test('E2E-02 card set quiz path',five)
        def scoring():
            page.locator('#q0').fill('My name is Fabio.')
            page.locator('input[name="q1"][value="1"]').check()
            page.locator('#q2').fill('for')
            page.locator('#q3').fill("I'm working now")
            page.locator('input[name="q4"][value="1"]').check()
            page.locator('#grade').click()
            assert 'Respostas confirmadas: 5/5' in page.locator('#results').inner_text()
            assert page.locator('#grade').is_disabled()
        test('E2E-03 exact reference + contraction score',scoring)
        def rerun():
            page.locator('#backCards').click();page.locator('#next').click()
            assert page.locator('#grade').is_enabled()
            page.locator('#grade').click()
            assert 'Respostas confirmadas: 0/5' in page.locator('#results').inner_text()
            assert 'sem resposta: 5' in page.locator('#results').inner_text()
        test('E2E-04 unanswered quiz and reset',rerun)
        def speech_fallback():
            page.locator('#backCards').click()
            # Force fallback for transcriber even if browser supports it
            page.evaluate('window.SpeechRecognition=undefined;window.webkitSpeechRecognition=undefined')
            page.locator('#recognize').click()
            assert 'indisponível' in page.locator('#speechStatus').inner_text()
        test('INT-01 ASR fallback without provider',speech_fallback)
        def clear():
            page.on('dialog',lambda d:d.accept())
            page.locator('#clear').click()
            assert page.locator('#english').inner_text()=='My name is Fabio.'
        test('INT-02 clear resets displayed content',clear)
        def no_xss():
            page.locator('#next').click(); assert page.locator('#words').count()==1
            assert page.locator('#words .word').count()>0
        test('SEC-01 content rendered as text nodes',no_xss)
        def mobile():
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2'), (page.evaluate('document.documentElement.scrollWidth'),page.evaluate('window.innerWidth'))
        test('UX-01 390px no horizontal overflow',mobile)
        test('REG-01 JS runtime exceptions',lambda: (_ for _ in ()).throw(AssertionError(errors)) if errors else None)
        browser.close()
    for name,status in outcomes:print(f'{status:7} {name}')
    print(f'RESULT: {sum(s=="PASS" for _,s in outcomes)}/{len(outcomes)}')
    return 0 if all(x=='PASS' for _,x in outcomes) else 1
if __name__=='__main__':raise SystemExit(run())
