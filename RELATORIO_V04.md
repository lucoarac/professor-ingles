# Relatório V0.4 — evidências locais

## Implementação
Terceira unidade A1 com cinco cartões e cinco perguntas: do/does, doesn't, isn't, did + verbo base e going to. Conteúdo sujeito a revisão pedagógica humana. Total: 15 cartões, 3 avaliações.

## Testes executados
- Node.js: 7/7 testes unitários do avaliador.
- Chromium local com scripts incorporados: 9/9 verificações de qualidade e gravação simulada; 9/9 testes de regressão das aulas anteriores; 5/5 verificações da nova unidade.
- Medição de 30 cliques na interface automatizada: mediana 57,27 ms e p95 empírico 79,49 ms; não representa latência de voz ou rede.

## Limitações
Testes de navegador usam HTML injetado e não validam deploy, HTTPS, carregamento de arquivos via rede, Safari iOS, voz física, microfone real, persistência após recarga, nem pronúncia. CI remoto não executado. Não há certificação de proficiência nem curso A1–C2 completo.

## Próximo gate
Publicação e HTTP/HTTPS; persistência após recarga; Safari iOS e Chrome Android com áudio/microfone; revisão linguística; acessibilidade.
