# Validação — V0.6

## O que foi executado nesta entrega
- Testes Node: avaliador, persistência e variantes curriculares.
- Playwright/Chromium em HTML injetado: navegação, questionários, estado de Storage por test double, tratamento de erros e corridas de áudio simuladas.
- A execução de navegação real para `http://127.0.0.1` não foi possível neste ambiente: Chromium retornou `ERR_BLOCKED_BY_ADMINISTRATOR`. O teste HTTP foi mantido no pacote para execução em um ambiente sem essa política.

## Critérios ainda não aprovados
- Persistência em navegador real por recarga HTTP/HTTPS (teste bloqueado neste ambiente; teste de contrato e unitário passaram).
- Safari iOS e Chrome Android em hardware físico; TTS, vozes, microfone, permissões e interrupções reais.
- Pronúncia avaliada foneticamente e avaliação semântica aberta de escrita.
- Acessibilidade manual/automatizada com leitor de tela, teclado, contraste e zoom.
- Revisão pedagógica independente e cobertura curricular integral A1–C2.
- Deploy público, HTTPS externo e CI remoto.

## Interpretação
Testes simulados confirmam apenas a lógica exercitada com mocks. Não equivalem a testes de hardware, SaaS de voz, homologação de navegador móvel ou autorização de produção.


## Complemento V0.7 — diagnóstico em dispositivo
- `diagnostics.html` foi incluído para validar persistência após recarga real, vozes do sistema, microfone/gravação e disponibilidade de reconhecimento.
- `tests/test_diagnostics.py`: 10/10 verificações estáticas.
- `tests/test_diagnostics_browser.py`: 9/9 verificações DOM com APIs de áudio simuladas.
- Esses testes não equivalem à execução do diagnóstico em Safari iOS ou Chrome Android físicos.
- O teste de `localStorage` após reload continua sem aprovação neste ambiente: Chromium bloqueia a navegação localhost. Use a página de diagnóstico numa origem HTTPS/localhost suportada e guarde o JSON exportado de cada dispositivo.
