# Relatório verificável de evolução V0.3 — 31/10/2026

## Escopo implementado
- Segunda aula A1 com 5 cartões explicativos e 5 avaliações; total de 10 cartões e 10 questões em duas unidades.
- Motor determinístico de correção extraído em `src/evaluator.js` com testes unitários Node.
- Resposta escrita desconhecida não recebe erro absoluto: entra como `review`, sem pontuação atribuída.
- Seleção de unidade e progresso local por posição/ID de unidade.
- Interface não exige assinatura, IA remota ou conta.

## Evidências e limites
- Teste de `node --test` com 7 casos unitários passou na execução local.
- Teste Playwright Chromium incorporando scripts passou nos casos de navegação, unidade 2, quiz 5/5, status de revisão, exceções no fluxo e largura móvel simulada. Não há áudio real testado.
- Tentativa de abrir localhost pelo Chromium falhou `ERR_BLOCKED_BY_ADMINISTRATOR` por política deste ambiente. Testes de reload/persistência real, HTTP/HTTPS externo, iOS Safari, gravação e TTS/STT real permanecem `NOT_RUN`.
- A qualidade pedagógica das novas explicações não passou por revisão humana especializada; validação editorial permanece pendente.
- A arquitetura ainda mistura UI e cards da aula 1 em `index.html`; extração total para módulos TypeScript segue pendente.

## Gargalos e riscos remanescentes
1. Não existe avaliação oral obrigatória nem rubrica fonética confiável (P0).
2. TTS nativo não possui sincronização por palavra nem controle de qualidade de voz (P0).
3. Uma escrita válida não cadastrada demanda revisão humana: sem serviço de revisão, fica sem nota (P0).
4. Testes HTTP/HTTPS, persistência real, dispositivo físico e acessibilidade são pré-requisitos de homologação (P0).
5. 10 cartões não são curso completo; cobertura A1–C2 e diálogos seguem no planejamento (P1).
6. Materiais precisam ser versionados e submetidos a revisão linguística antes de se tornarem conteúdo aprovado (P1).
7. CI definida, mas nunca executada no GitHub; sem green build remoto (P1).

## Próximos gates
G1: subir repositório e passar testes em CI; G2: publicar HTTPS e verificar acesso; G3: validar mic/TTS no Safari iOS e Android; G4: rubricas e revisão linguística; G5: expandir módulos sem perder regressão.
