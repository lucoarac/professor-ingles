# Relatório de testes — 2026-10-31

- **PASS**: verificação estática de cinco cartões, cinco questões, API de voz, captura, transcrição, nota e progresso.
- **PASS**: renderização no Chromium headless com `set_content`; navegação dos cinco cartões; correção de três respostas escritas e duas de múltipla escolha, total 5/5; sem erros JavaScript de página nesse fluxo.
- **PASS**: verificação sintática do JavaScript via `node --check` para o script extraído.
- **NÃO TESTADO**: vozes reais PT-BR e en-US; reprodução, microfone, transcrição e permissões nos dispositivos reais; persistência após reload em origem de servidor. O ambiente de navegador automatizado bloqueou acesso HTTP local e file:// por política administrativa, então o teste foi feito com HTML injetado; não representa um E2E completo.
- **NÃO IMPLEMENTADO**: os outros níveis, servidor, contas, análise fonética, PWA, pipeline CI/CD e observabilidade de produção.
