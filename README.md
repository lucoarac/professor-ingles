# Professor de Inglês — V0.7 de laboratório

**Não homologado para produção.** Quatro unidades A1 implementadas (20 cartões e 20 questões). O produto ainda não constitui um curso A1 completo; os demais níveis seguem planejados. Professor em português, síntese de voz nativa, gravação local opcional e transcrição do navegador com aviso antes do possível envio remoto.

## Executar por HTTP local
Na pasta do projeto: `python -m http.server 8000` e abrir `http://localhost:8000/`. O `localhost` é origem de desenvolvimento apropriada para APIs que exigem contexto seguro. Não usar `file://` como ambiente de validação.

## Persistência e privacidade
- Posição atual e resultados agregados por unidade são salvos em `localStorage` versionado (`english-professor-state-v1`).
- Respostas livres, gravações e transcrições não são gravadas no armazenamento local pela aplicação.
- O estado antigo é migrado quando válido; JSON inválido e versões desconhecidas não são sobrescritos na inicialização.
- Armazenamento bloqueado/cheio gera aviso; sem storage, a sessão continua, mas o progresso pode ser perdido ao fechar a página.
- O estado local não sincroniza entre aparelhos, navegadores, perfis, origens HTTP e HTTPS.
- Reconhecimento de fala é opcional; alguns navegadores enviam áudio a um serviço remoto. A aplicação informa esse risco antes de iniciar a transcrição. Não há avaliação fonética.

## Diagnóstico em dispositivo real
Abra `diagnostics.html` na mesma origem HTTPS (ou localhost) usada para testar o app. A página permite verificar se `localStorage` sobrevive a uma recarga real, listar vozes, solicitar permissão do microfone, gravar/reproduzir um trecho de 2 segundos e verificar disponibilidade de reconhecimento de fala. Nenhum teste de áudio inicia sozinho; o reconhecimento exige confirmação explícita. A gravação fica somente na memória da página e o relatório JSON exportado não inclui áudio nem texto transcrito. Use esta página em Safari iOS e Chrome Android para coletar evidência real; um resultado em desktop não comprova o outro dispositivo.

## Testes reproduzíveis
Requisitos: Node.js 22, Python 3.12+, Playwright Python e Chromium. Para preparar o ambiente de testes:

```powershell
py -m pip install -r requirements-dev.txt
py -m playwright install chromium
```

Para servir o app no Windows (PowerShell), execute na pasta do projeto `py -m http.server 8000` e abra `http://localhost:8000/`.

```bash
node --test tests/evaluator.test.js tests/persistence.test.js tests/content.test.js
python tests/test_ui.py
python tests/test_v03_browser.py
python tests/test_unit3_browser.py
python tests/test_unit4_browser.py
python tests/test_browser_storage_shim.py
python tests/test_audio_lifecycle.py
python tests/test_accessibility_primitives.py
python tests/test_persistence_http.py
python tests/test_quality.py
python tests/test_diagnostics.py
python tests/test_diagnostics_browser.py
```

`test_persistence_http.py` inicia um servidor HTTP local e tenta testar navegação, recarga real, conclusão e reinício. Requer que a política do ambiente permita Chromium acessar localhost. Se o navegador bloquear a navegação, a suíte marca a etapa como bloqueada (código de saída 77), não como aprovada. `test_browser_storage_shim.py` verifica a integração da aplicação com a interface Storage simulada; não substitui a verificação nativa por HTTP. Os testes de voz usam simulação quando indicado; não comprovam microfone, TTS ou reconhecimento em aparelho físico. Os testes de acessibilidade verificam semântica de progresso, idioma, foco e dois pares de contraste; não substituem auditoria WCAG/VoiceOver.

## Política de correção
Questões objetivas são avaliadas deterministicamente. Questões de escrita aceitam somente variantes cadastradas e normalizadas; uma resposta diferente é encaminhada para revisão, não reprovada como errada. Isso reduz falsos negativos sem fingir que há avaliação semântica. Não existe nota de pronúncia.

## Limitações conhecidas
Sem autenticação, backend, sincronização, avaliação semântica por IA, avaliação fonética, revisão editorial independente, homologação WCAG, teste de Safari iOS/Android em hardware real, deploy público ou execução de CI remota comprovados.
