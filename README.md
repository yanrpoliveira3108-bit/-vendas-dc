# Bot de vendas para Discord

Bot inicial em Node.js + discord.js com:
- catálogo e painel de vendas;
- carrinho por usuário;
- criação de pedido e QR de PIX;
- aprovação/recusa manual pela equipe;
- SQLite local;
- endpoint `/health`.

## Instalação
1. Instale Node.js 20+.
2. Rode `npm install`.
3. Copie `.env.example` para `.env` e preencha as variáveis.
4. Convide o bot com os escopos `bot` e `applications.commands`, com permissões para enviar mensagens, anexar arquivos e usar componentes.
5. Rode `npm run deploy`.
6. Rode `npm start`.

## Uso
- `/produto-add nome preco descricao` cadastra produtos (preço em reais).
- `/painel-vendas` publica o painel.
- O cliente adiciona produtos e finaliza pelo botão **Ver carrinho**.
- A equipe confere o PIX e usa `/pedido-aprovar id` ou `/pedido-recusar id`.

## Próximos aprimoramentos recomendados
- Integrar Mercado Pago/PagSeguro via webhook para aprovação automática.
- Criar tabela de estoque/entrega e enviar cargos, keys ou arquivos automaticamente.
- Adicionar logs privados, tickets e proteção contra duplicidade de pagamento.
- Para produção, usar PostgreSQL e armazenar segredos em variáveis do servidor.

> O payload PIX incluído é uma base simples para protótipo; para cobrança PIX válida com identificador e conciliação automática, use uma API de pagamentos.
