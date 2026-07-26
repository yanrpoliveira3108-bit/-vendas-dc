import 'dotenv/config';
import { REST, Routes, SlashCommandBuilder } from 'discord.js';
const commands=[
 new SlashCommandBuilder().setName('painel-vendas').setDescription('Publica o painel da loja'),
 new SlashCommandBuilder().setName('produto-add').setDescription('Cadastra produto').addStringOption(o=>o.setName('nome').setDescription('Nome').setRequired(true)).addNumberOption(o=>o.setName('preco').setDescription('Preço em BRL').setRequired(true)).addStringOption(o=>o.setName('descricao').setDescription('Descrição').setRequired(true)),
 new SlashCommandBuilder().setName('produto-remover').setDescription('Desativa produto').addIntegerOption(o=>o.setName('produto').setDescription('ID').setRequired(true)),
 new SlashCommandBuilder().setName('estoque-add').setDescription('Adiciona URL/key ao estoque').addIntegerOption(o=>o.setName('produto').setDescription('ID').setRequired(true)).addStringOption(o=>o.setName('conteudo').setDescription('URL privada ou key').setRequired(true)),
 new SlashCommandBuilder().setName('estoque-ver').setDescription('Consulta estoque').addIntegerOption(o=>o.setName('produto').setDescription('ID').setRequired(true)),
 new SlashCommandBuilder().setName('pedido-aprovar').setDescription('Aprova e entrega pedido').addStringOption(o=>o.setName('id').setDescription('ID').setRequired(true)),
 new SlashCommandBuilder().setName('pedido-recusar').setDescription('Recusa pedido').addStringOption(o=>o.setName('id').setDescription('ID').setRequired(true))
].map(x=>x.toJSON());
const rest=new REST({version:'10'}).setToken(process.env.DISCORD_TOKEN);
await rest.put(Routes.applicationGuildCommands(process.env.CLIENT_ID,process.env.GUILD_ID),{body:commands}); console.log('Comandos publicados.');
