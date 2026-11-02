# Auditoria técnica V0.2 — 31/10/2026

## Escopo real
Auditoria do arquivo `index.html` recebido do pacote `professor-ingles-github-v01`, sem presumir funcionalidades inexistentes. Não houve acesso a dispositivos físicos, deploy público nem backend. A primeira aula contém exatamente 5 cartões e 5 questões.

## Ambiente e método
- Python Playwright controlando Chromium em contêiner; carregamento do conteúdo HTML diretamente via `page.set_content` pois navegação local foi bloqueada.
- Verificações de interface visível: navegação, progressão para quiz, alternativas e escrita, nota 5/5 e 0/5, repetição, indisponibilidade ASR, reset, responsividade a 390 px, erros de console.
- Simulação controlada de MediaRecorder/getUserMedia para validar liberação de tracks ao navegar. Não testa microfone real.
- Verificações estáticas de markup e chamadas de rede; **não** equivalem a revisão completa de segurança.
- Latência de 30 interações em Chromium headless por clique+atualização DOM; **não** representa cold-start, aparelho móvel, rede ou síntese de voz.

## Falhas encontradas e corrigidas
1. `clear` executava `localStorage.removeItem` sem tratamento de exceção; em contexto restrito a página lançava erro e não reiniciava corretamente. Adicionado `try/catch`. **Reproduzido: falhou na primeira execução, passou no reteste**.
2. Gravação continuava ao navegar, arriscando gravação indevida e recursos do microfone abertos. Foi adicionado `stopRecording` e invalidação de sessão ao trocar de cartão. **Verificado com microfone simulado**.
3. Solicitação de microfone assíncrona poderia terminar depois de o aluno navegar; adicionada validação de revisão e descarte da stream obsoleta. **Implementado; corrida específica ainda sem teste automatizado**.
4. `Parar voz` não invalidava a sequência de explicação, que poderia retomar a frase inglesa; agora invalida a revisão ativa. **Correção implementada; precisa teste de síntese real**.
5. Resposta tardia do transcritor podia atualizar um cartão novo; resultado é ignorado se a revisão mudou. **Implementado; teste de corrida pendente**.
6. Gravação anterior ficava associada ao cartão novo; URL é revogada e reprodução desabilitada ao sair. Callback tardio de término é ignorado por revisão de sessão. **Implementado; testar em Safari físico**.

## Resultado automatizado local
- `python tests/test_ui.py`: **9/9 PASS** (depois de dois erros iniciais corrigidos).
- `python tests/test_quality.py`: **9/9 PASS**, sendo 6 checks estáticos e 3 checks de UI/gravador simulado.
- Total: **18/18 checagens aprovadas** da suíte atual. Não significa 18 requisitos completos nem aprovação para produção.
- Amostra de 30 cliques de UI: mediana **35–46 ms** e p95 empírico **49–78 ms** em duas execuções (30 interações por execução) na máquina da auditoria, incluindo overhead do Playwright; não usar como SLA da aplicação real.

## Bloqueios críticos ainda existentes — NÃO homologar
**P0 — viabilidade e segurança da experiência:**
- Professor virtual ainda não destaca cada palavra em sincronia com o áudio; utiliza a voz genérica do dispositivo.
- Avaliação de fala não é pontuada; exercício oral não é exigido na avaliação (apenas gravação opcional).
- ASR pode estar ausente ou processar áudio remotamente; não há consentimento granular nem política revisada.
- A correção de escrita usa somente correspondência literal após normalização; falsos negativos para respostas linguisticamente válidas.
- Não existe teste ponta-a-ponta navegando na URL HTTPS publicada, nem teste físico Safari iOS/Android.

**P1 — funcionalidade pedagógica:**
- Escuta não possui avaliação real; ver texto na tela pode permitir acertar sem compreender áudio.
- Apenas cinco cartões A1 e um teste de cinco itens. Não há currículo completo, banco de questões, revisão espaçada, alternância de níveis, acompanhamento por habilidade, teste diagnóstico, feedback individual, diálogos ou conversação livre.
- Conjugação verbal é incidental, sem matriz sistemática tempos/aspectos, pessoa, modo, auxiliares, pergunta/negação, exceções e exercícios por contexto.
- Fonética aproximada sem IPA/áudio humano validado e sem avaliação de sotaques.
- Persistência salva posição e último resultado, mas não histórico por habilidade; não permite multiusuário/sincronização.

**P1 — qualidade/DevOps:**
- Script e conteúdo estão monolíticos; faltam esquema tipado, separação domínio/infra/UI, migrations, lint, testes unitários independentes, testes de integração de contrato, mocks determinísticos abrangentes, testes de regressão isolados e cobertura instrumentada.
- Testes UI atuais encadeiam estados no mesmo browser; precisam ser convertidos em cenários independentes com storage isolado.
- Sem auditoria automática `axe-core`, leitor de tela real, foco de teclado, tamanhos de toque WCAG 2.2, contraste e zoom até 200%.
- Sem métricas RUM Core Web Vitals, monitoramento de erros, laboratório de rede lenta, battery/memory leak, carga concorrente ou pipeline de release com gates.
- Sem CSP explícita, definição de dependências, SAST, proteção de branch e políticas documentadas de privacidade/retenção de áudio.

## Matriz de testes que falta construir
| Camada | Casos de teste / evidência requerida | Critério proposto | Situação |
|---|---|---|---|
| Unitário | normalização e rubrica com gabarito validado, acentos, contrações, tempos | determinístico; sem falsos positivos de gramática | Pendente |
| Componente | card, player, progresso, questionário, foco | estados de erro e transições | Parcial |
| Integração | áudio+quadro, player+cancelamento, gravação+troca de cartão, persistência | recursos liberados e feedback coerente | Parcial com mocks |
| Contrato | APIs TTS/STT e respostas de erro | schema versionado/tempo limite/retry limitado | Não aplicável ainda |
| E2E | primeiro acesso → 5 cartões → fala → escrita → nota → revisão → recarregar | tudo em HTTPS com dados reais | Pendente |
| Regressão | repetição automatizada dos fluxos já aprovados | 0 regressão crítica | Parcial |
| Cross-browser | Safari iOS, Chrome Android, Chromium desktop, Firefox | fluxo essencial independente de ASR | Pendente |
| Acessibilidade | teclado, VoiceOver, contraste, WCAG 2.2 AA | sem barreiras críticas; avaliação humana | Pendente |
| Segurança | CSP, XSS, controle de acesso, consentimento áudio, SBOM | zero achado crítico/alto não tratado | Pendente |
| Performance | TTFB/LCP/INP/CLS, latência voz, consumo memória, aparelhos fracos | limites definidos após baseline em dispositivos reais | Pendente |
| Carga | concorrência TTS/STT/backend | sem degradação acima de SLO aprovado | Não aplicável ao protótipo estático |
| Resiliência | offline/voz ausente, microfone negado, interrupção, recarga, aba em background | fallback sem perda de aprendizado | Parcial |
| Pedagógico | especialistas validam erros/exemplos/nível CEFR | rubrica de revisão editorial aprovada | Pendente |
| Qualidade ASR | ruído, sotaques brasileiros, falsos negativos, WER/CER por grupo | limiares após dataset rotulado; não presumidos | Pendente |

## Projeto técnico sem achismos
Aprovar primeiro o motor pedagógico, depois a infraestrutura: conteúdo em JSON/TS validado com schema; versionamento editorial e testes de exemplos; UI desacoplada de `SpeechProvider`; `SpeechProvider` inicial com TTS nativo e capacidade de mudar para serviço remoto mediante decisão explícita, termos/consentimento e custo. Não adicionar Supabase até a necessidade real de sincronizar histórico; não adicionar Twilio para voz de aula sem benchmark.

## Política de classificação
`PASS`: execução reproduzível com assert; `FAIL`: falha observada; `NOT_RUN`: não testado; `BLOCKED`: ambiente impede; `DESIGN`: planejamento, sem implementação. Nunca chamar `DESIGN` de funcionalidade pronta.

---

# Atualização V0.6 — 31/10/2026

A implementação V0.6 resolveu parcialmente os itens de persistência, variantes de escrita e gestão de sessão de áudio descritos acima. O detalhe dos testes executados e bloqueios encontra-se em `RELATORIO_V06.md`.

| Item do V0.5 | Estado V0.6 | Evidência / limite |
|---|---|---|
| Persistência local de posição e resultados | **IMPLEMENTADO; reload nativo ainda NOT_RUN** | Módulo versionado, migração, validação, limpeza e testes unitários; navegador bloqueou navegação localhost |
| Variações de escrita | **PARCIAL** | Variantes específicas cadastradas e testadas; texto livre fora do catálogo segue para revisão |
| Corrida de permissão de microfone | **TESTADO COM MOCK** | Stream tardia é descartada e tracks encerradas |
| Reconhecimento/transcrição após trocar cartão | **TESTADO COM MOCK** | `abort()` na troca e callbacks antigos ignorados |
| Consentimento de transcrição | **IMPLEMENTADO** | Confirmação antes da primeira ativação na sessão; não equivale a revisão jurídica/política completa |
| Microfone/TTS/Safari físico | **NOT_RUN** | Requer aparelhos e navegadores reais |
| Acessibilidade primitiva | **TESTADO PARCIALMENTE** | Progressbar, idioma, status, foco e dois pares de contraste passaram 11/11; sem axe/WCAG/VoiceOver |
| Deploy público/CI remoto | **NOT_RUN** | Workflow de qualidade está no repositório, sem evidência de execução remota; nenhum deploy configurado |


## Adendo V0.7 — instrumento de homologação em dispositivo

A V0.7 adiciona `diagnostics.html`, uma página local sem dependências externas para coletar evidência do navegador real. O teste de persistência utiliza chave própria e sobrevive a uma recarga real; os testes de voz e microfone são acionados manualmente; o reconhecimento exige consentimento explícito devido à possibilidade de processamento remoto. O relatório exportado não inclui áudio nem texto transcrito.

A página foi verificada por 10 testes estáticos e 9 verificações DOM com APIs de áudio simuladas. Esses resultados não homologam hardware. O bloqueio de navegação Chromium para localhost permanece e a persistência nativa após reload ainda requer execução em ambiente externo permitido.
