import 'dotenv/config';
import { REST, Routes, SlashCommandBuilder } from 'discord.js';

const commands = [
  new SlashCommandBuilder().setName('painel-vendas').setDescription('Publica o painel de produtos e carrinho'),
  new SlashCommandBuilder().setName('produto-add').setDescription('Adiciona um produto').addStringOption(o=>o.setName('nome').setDescription('Nome').setRequired(true)).addNumberOption(o=>o.setName('preco').setDescription('Preço em BRL').setRequired(true)).addStringOption(o=>o.setName('descricao').setDescription('Descrição').setRequired(true)),
  new SlashCommandBuilder().setName('pedido-aprovar').setDescription('Aprova um pedido após conferir o PIX').addStringOption(o=>o.setName('id').setDescription('ID do pedido').setRequired(true)),
  new SlashCommandBuilder().setName('pedido-recusar').setDescription('Recusa um pedido').addStringOption(o=>o.setName('id').setDescription('ID do pedido').setRequired(true))
].map(c=>c.toJSON());
const rest = new REST({version:'10'}).setToken(process.env.DISCORD_TOKEN);
await rest.put(Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID), {body:commands});
console.log('Comandos publicados.');
