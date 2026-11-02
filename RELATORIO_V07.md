# Relatório técnico V0.7 — diagnóstico verificável em dispositivo

Data: 31/10/2026  
Base: V0.6, sem alterar o currículo ou o avaliador de respostas.

## Objetivo

A V0.6 já continha um teste E2E de `localStorage` por HTTP, mas o Chromium do ambiente de desenvolvimento bloqueou tanto HTTP localhost quanto `file://` com `ERR_BLOCKED_BY_ADMINISTRATOR`. Não havia evidência para declarar a persistência nativa aprovada. Como a limitação é da política de execução, não do código da aplicação, a V0.7 acrescenta um instrumento independente para executar os testes no navegador real que será utilizado pelo aluno.

## Implementação

Criado `diagnostics.html`, sem dependências externas, com quatro verificações controladas pelo usuário:

1. **Persistência após recarga real:** grava um marcador temporário em chave própria e em `sessionStorage`, recarrega a página e compara o valor recuperado. Não toca na chave de progresso do curso.
2. **Síntese de voz:** lista vozes fornecidas pelo sistema e permite reproduzir uma frase de teste.
3. **Microfone e gravação:** somente após clique, solicita permissão, grava aproximadamente dois segundos, encerra as tracks e permite ouvir o resultado. O áudio permanece em memória e não é enviado nem armazenado pela aplicação.
4. **Reconhecimento de fala:** só inicia após confirmação explícita sobre possível processamento remoto. A transcrição não é apresentada como nota de pronúncia.

O relatório JSON exportável contém dados de ambiente e estados dos testes; não inclui áudio nem transcrição. A ferramenta não depende de backend, analytics ou chamadas de rede externas.

## Testes executados nesta etapa

- Testes Node da V0.6: 16/16 aprovados.
- Regressão de UI: 9/9.
- Regressão unidades 1 e 2: 9/9.
- Unidade 3: 5/5.
- Unidade 4: 6/6.
- Contrato de Storage simulado: 7/7.
- Ciclo de áudio simulado: 8/8.
- Acessibilidade básica: 11/11.
- Qualidade: 9/9.
- Novo teste estático da página de diagnóstico: 10/10.
- Novo teste DOM/Playwright da página de diagnóstico, com APIs de áudio simuladas: 9/9.
- E2E HTTP nativo: servidor respondeu HTTP 200; navegação Chromium bloqueada pelo ambiente (exit code 77). Não aprovado / não executado.

As contagens são por suíte e podem se sobrepor. O teste novo estático confirma guardrails e presença de funcionalidades, não o funcionamento em hardware real.

## Próxima execução de homologação

Abrir `diagnostics.html` servido pela mesma origem HTTPS do app em:

- Safari iOS real: persistência após reload, vozes, permissão do microfone, gravação/reprodução e interrupção.
- Chrome Android real: os mesmos casos.

Guardar o JSON exportado de cada dispositivo, sem áudio ou transcrição. Comparar capacidades por navegador/SO e só então decidir se há suporte de produto ou fallback. A execução física não foi realizada nesta etapa.

## Limitações

A V0.7 não resolve a falta de dispositivo físico nem a política que bloqueia navegação Chromium neste ambiente. Não há evidência de Safari/Android, deploy HTTPS, CI remota executada, revisão de privacidade/jurídica do ASR, avaliação fonética, avaliação semântica geral ou homologação de produção.
