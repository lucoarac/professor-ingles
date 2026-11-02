from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'diagnostics.html').read_text(encoding='utf-8')
checks = []
def verify(name, condition):
    checks.append(bool(condition))
    print(('PASS ' if condition else 'FAIL ') + name)

verify('Página de diagnóstico declara pt-BR', '<html lang="pt-BR">' in html)
verify('Teste de persistência usa chave própria, separada do progresso', 'english-professor-diagnostic-reload-v1' in html and 'english-professor-state-v1' not in html)
verify('Persistência é verificada somente após reload', 'location.reload()' in html and 'verifyReload()' in html)
verify('Microfone depende de clique explícito', "$('recordTest').addEventListener('click'" in html)
verify('Reconhecimento exige confirmação explícita', 'confirm(' in html and "$('recognizeTest').addEventListener('click'" in html)
verify('Gravação encerra tracks de áudio', 'stream.getTracks().forEach(t=>t.stop())' in html)
verify('Nenhuma chamada de upload/fetch/XHR', not re.search(r'\b(fetch|XMLHttpRequest|sendBeacon)\s*\(', html))
verify('Exportação exclui texto transcrito e áudio', "report.tests.speechRecognition='result-received'" in html and 'report.recordingMimeType' in html and 'transcript:' not in html)
verify('Aviso sobre possível processamento remoto está presente', 'serviço remoto' in html)
verify('Relatório não inclui áudio codificado', 'FileReader' not in html and 'base64' not in html)
print(f'RESULT {sum(checks)}/{len(checks)}')
assert all(checks)
