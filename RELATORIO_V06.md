# Relatório técnico V0.6 — correção dos bloqueios priorizados

Data: 31/10/2026  
Base: pacote V0.5, preservando as quatro unidades A1 já existentes.

## 1. Escopo desta entrega

Prioridade definida a partir dos bloqueios descritos no relatório V0.5: persistência local, correção de respostas escritas e gestão do ciclo de vida de gravação/transcrição. Não foi iniciada expansão de conteúdo enquanto esses bloqueios eram tratados.

## 2. Implementações realizadas

### 2.1 Persistência local versionada

- Criado `src/persistence.js`, isolando a persistência da interface.
- Estado versionado em `english-professor-state-v1`.
- Guarda somente posição (unidade/cartão) e resumos agregados das avaliações concluídas.
- Não grava respostas textuais livres, gravações ou transcrições.
- Valida versão, índices de unidade/cartão, totais e data de conclusão ao carregar.
- Faz migração dos formatos legados V0.5 quando válidos.
- Trata armazenamento indisponível, JSON corrompido, versão incompatível e quota excedida sem derrubar a sessão.
- Mostra na interface quantas unidades foram concluídas e avisa que o dado é local, sem sincronização entre aparelhos.
- O reset remove a chave atual e as chaves legadas.

**Decisão técnica:** `localStorage` é suficiente para o volume atual (posição e pequenos resumos). Não foi introduzido IndexedDB, Supabase ou backend, porque o requisito atual não inclui grande volume de dados nem sincronização. Se houver contas/sincronização, a arquitetura deve ser reavaliada.

### 2.2 Avaliação de escrita

- Mantida a política conservadora: só variantes cadastradas são aprovadas automaticamente.
- Acrescentadas equivalências específicas e revisadas no conjunto A1 existente, como `She works at/in the store`, `He's not at home`, `I study English daily` e formas numéricas/por extenso para horários.
- Uma resposta não reconhecida continua em `review`, não em `incorrect`.
- A aplicação não tenta deduzir equivalência semântica com similaridade textual ou pontuação fuzzy.

**Limite mantido:** ainda não existe avaliador semântico de escrita. Novas formulações não cadastradas podem exigir revisão humana.

### 2.3 Ciclo de vida de áudio e transparência

- Reconhecimento de fala exige confirmação explícita antes da primeira ativação da sessão, informando que alguns navegadores podem enviar áudio a serviço remoto e que a transcrição não gera nota de pronúncia.
- Transcrição ativa é abortada quando o aluno troca de cartão ou encerra a atividade.
- Callbacks atrasados de reconhecimento não podem escrever resultado em cartão posterior.
- Permissão de microfone obtida após o aluno navegar é descartada, com tracks encerradas.
- Falhas de permissão, ausência de microfone e indisponibilidade/erro do `MediaRecorder` têm feedback mais específico.
- Se a criação do `MediaRecorder` falhar após obter a stream, as tracks são encerradas.

**Limite mantido:** nenhum desses testes substitui a verificação em microfone físico ou Safari/Chrome móveis.

## 3. Evidência de testes executados

### Node.js

`node --test tests/evaluator.test.js tests/persistence.test.js tests/content.test.js`  
**16/16 aprovados.** Inclui normalização do avaliador, respostas desconhecidas encaminhadas para revisão, salvamento/recuperação, migração, corrupção, versão incompatível, bloqueio de storage, quota e limpeza.

### Chromium / Playwright com scripts locais e APIs simuladas

| Suíte | Resultado | Escopo |
|---|---:|---|
| `tests/test_ui.py` | 9/9 | Navegação, avaliação, fallback ASR, reset, DOM e largura móvel de 390 px |
| `tests/test_v03_browser.py` | 9/9 | Regressão das unidades 1 e 2, questionário e resposta em revisão |
| `tests/test_unit3_browser.py` | 5/5 | Fluxo e avaliação da unidade 3 |
| `tests/test_unit4_browser.py` | 6/6 | Fluxo e avaliação da unidade 4 |
| `tests/test_browser_storage_shim.py` | 7/7 | Integração da interface com contrato Storage simulado, posição, resultado e reset |
| `tests/test_audio_lifecycle.py` | 8/8 | Corridas de permissão, liberação de tracks, consentimento, aborto e falhas simuladas |
| `tests/test_accessibility_primitives.py` | 11/11 | Semântica do progresso, idioma, status, foco, nomes de campos e dois pares de contraste |
| `tests/test_quality.py` | 9/9 | Verificações estáticas e gravação simulada |

As contagens são verificações por suíte e há sobreposição entre cenários. Não devem ser interpretadas como casos E2E independentes. Os mocks comprovam somente os fluxos de código exercitados.

### HTTP e recarga real

- O servidor Python respondeu `HTTP 200` para `/index.html`.
- A tentativa de navegação do Chromium para `http://127.0.0.1` retornou `ERR_BLOCKED_BY_ADMINISTRATOR` neste ambiente de execução.
- Resultado: **BLOCKED / NOT_RUN** para a recarga real do navegador por HTTP. O teste automatizado (`tests/test_persistence_http.py`) foi mantido para rodar em ambiente sem a política que bloqueia localhost.
- O teste com Storage test double e os testes unitários passaram, mas não substituem o E2E de armazenamento nativo no navegador.

### Desempenho local observado

Amostra de 30 transições clique + atualização DOM em Chromium headless: mediana **33,64 ms**, p95 empírico **45,39 ms**. É uma medição local de interação simplificada, não SLA, não Core Web Vitals e não representa dispositivo móvel, rede ou áudio.

## 4. Bloqueios remanescentes — não homologar

1. E2E de armazenamento `localStorage` nativo após reload em HTTP/HTTPS, pois a política do ambiente bloqueou a navegação Chromium para localhost.
2. Testes físicos em Safari iOS e Chrome Android: permissões, gravação, reprodução, TTS, vozes disponíveis, interrupção e troca de aplicativo/aba.
3. Reconhecimento de fala tem disponibilidade variável entre navegadores e pode utilizar serviço remoto; ainda não existe contrato com provedor dedicado, política jurídica/privacidade revisada ou teste offline.
4. Não há avaliação acústica/fonética de pronúncia. ASR é somente transcrição aproximada, jamais nota de pronúncia.
5. Avaliação escrita não é semântica; respostas fora da lista aprovada são encaminhadas para revisão.
6. A acessibilidade foi verificada apenas em atributos e pares de contraste selecionados; VoiceOver, leitor de tela, teclado completo, zoom e auditoria WCAG continuam pendentes.
7. O currículo entregue permanece limitado a 4 unidades A1, 20 cartões e 20 questões. Não representa o nível A1 integral nem níveis A2–C2.
8. Não há backend, autenticação, sincronização, monitoramento, deploy público ou evidência de CI remoto executado.
9. Conteúdo e explicações ainda requerem revisão editorial independente por professor de inglês.

## 5. Referências técnicas primárias

- MDN — `localStorage`: armazenamento persistente por origem e exceções de acesso: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
- MDN — `SpeechRecognition`: disponibilidade limitada e possibilidade de processamento remoto: https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition
- MDN — `getUserMedia()`: requisito de contexto seguro e permissão de usuário: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia

## 6. Conclusão

V0.6 melhora a persistência local, explicita estados de falha, reduz falsos negativos previsíveis em respostas escritas e fecha corridas de gravação/transcrição cobertas por mocks. **A entrega continua sendo um protótipo de laboratório.** A recarga real em navegador, compatibilidade móvel física, qualidade pedagógica independente, acessibilidade e publicação ainda não foram homologadas.
