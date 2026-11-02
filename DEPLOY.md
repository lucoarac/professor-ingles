# Publicação — estado atual

O projeto é um site estático e pode ser hospedado sem backend para as funções atuais. **Nenhum deploy está configurado ou realizado nesta versão.**

O workflow incluído (`.github/workflows/ci.yml`) chama-se `Quality checks` e executa testes; ele não publica o site. Para publicar posteriormente, será necessário configurar GitHub Pages (ou outro host estático), criar um workflow de deploy separado e validar a URL HTTPS externa.

Antes de habilitar publicação: decidir se o repositório/código/conteúdo será público; revisar privacidade e termos para reconhecimento de voz; confirmar execução dos quality checks; testar Safari iOS e Chrome Android em dispositivos reais.

A aplicação ainda não tem autenticação, backend, sincronização, monitoramento ou infraestrutura de produção.
