# Relatório V0.5 — implementação e testes

## Implementação
- Adicionada Aula 4 A1 com cinco cartões: presente simples, presente contínuo, passado simples, passado contínuo e futuro com will.
- Cada cartão inclui tradução, pronúncia aproximada, análise de palavras, explicação em português e exemplos.
- Adicionada avaliação de cinco questões.
- Atualizado seletor de aulas, carregamento de módulo e reinício de progresso.
- Atualizado CI para incluir teste da unidade 4.
- Corrigido teste de qualidade que rejeitava incorretamente a inclusão do novo script local `src/unit4.js`.

## Resultado da execução local
- Node.js evaluator: 7/7.
- Testes de qualidade e gravação simulada: 9/9.
- Regressão de fluxo das unidades anteriores: 9/9.
- Unidade 3: 5/5.
- Unidade 4: 6/6.
- Total: 36 verificações aprovadas, 0 falhas nas suítes concluídas.

A soma representa verificações de naturezas diferentes, não 36 testes E2E independentes. A gravação foi simulada com API falsa; não representa microfone físico.

## Desempenho observado
30 interações automatizadas clique + atualização DOM: mediana 42,88 ms; p95 empírico 52,41 ms. Medição em Chromium headless, sem rede, áudio ou hardware móvel. Não extrapolar para experiência real.

## Bloqueios não validados
- Persistência após reload em HTTP/HTTPS.
- Deploy público e acesso externo.
- TTS e seleção de vozes em dispositivos reais.
- Microfone físico, permissões e reprodução real em Safari iOS/Chrome Android.
- Pronúncia avaliada foneticamente.
- Acessibilidade manual com teclado/leitor de tela.
- CI remoto e segurança de infraestrutura.
- Revisão editorial independente do conteúdo.

## Próximo gate
Antes de adicionar mais volume:
1. Servir por HTTP local e testar persistência após reload.
2. Testar permissões, gravação e TTS em aparelhos reais.
3. Ampliar testes de correção para variações gramaticais válidas.
4. Executar auditoria de acessibilidade e regressão completa.
5. Só então expandir a próxima unidade curricular.
