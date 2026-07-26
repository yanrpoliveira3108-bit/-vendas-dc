import 'dotenv/config';
import express from 'express';
import QRCode from 'qrcode';
import Database from 'better-sqlite3';
import { Client, GatewayIntentBits, Events, ActionRowBuilder, ButtonBuilder, ButtonStyle, EmbedBuilder, StringSelectMenuBuilder, PermissionsBitField } from 'discord.js';

const db = new Database('store.db');
db.exec(`CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,description TEXT NOT NULL,price INTEGER NOT NULL,active INTEGER DEFAULT 1); CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY,user_id TEXT,channel_id TEXT,status TEXT,total INTEGER,items TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);`);
const brl = n => (n/100).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
const isAdmin = i => i.memberPermissions?.has(PermissionsBitField.Flags.ManageGuild) || (process.env.ADMIN_ROLE_ID && i.member?.roles?.cache?.has(process.env.ADMIN_ROLE_ID));
const client = new Client({intents:[GatewayIntentBits.Guilds]});
const carts = new Map();

function productEmbed(){
  const products=db.prepare('SELECT * FROM products WHERE active=1 ORDER BY id').all();
  return products.length ? products.map(p=>`**${p.id}. ${p.name}** — ${brl(p.price)}\n${p.description}`).join('\n\n') : 'Nenhum produto cadastrado ainda.';
}
function panel(){
  const products=db.prepare('SELECT * FROM products WHERE active=1 ORDER BY id').all();
  const menu=new StringSelectMenuBuilder().setCustomId('add_product').setPlaceholder('Selecione um produto').addOptions(products.slice(0,25).map(p=>({label:p.name.slice(0,100),description:`${brl(p.price)} • ID ${p.id}`,value:String(p.id)})));
  return {embeds:[new EmbedBuilder().setTitle('🛒 Loja').setDescription(productEmbed()).setColor(0x5865f2)],components:products.length?[new ActionRowBuilder().addComponents(menu),new ActionRowBuilder().addComponents(new ButtonBuilder().setCustomId('view_cart').setLabel('Ver carrinho').setStyle(ButtonStyle.Primary))]:[]};
}
client.on(Events.InteractionCreate, async i=>{
 try {
  if(i.isChatInputCommand()){
   if(i.commandName==='painel-vendas'){await i.channel.send(panel()); return i.reply({content:'Painel publicado.',ephemeral:true});}
   if(['produto-add','pedido-aprovar','pedido-recusar'].includes(i.commandName)&&!isAdmin(i)) return i.reply({content:'Sem permissão.',ephemeral:true});
   if(i.commandName==='produto-add'){const p=db.prepare('INSERT INTO products(name,description,price) VALUES(?,?,?)').run(i.options.getString('nome'),i.options.getString('descricao'),Math.round(i.options.getNumber('preco')*100));return i.reply({content:`Produto #${p.lastInsertRowid} cadastrado.`,ephemeral:true});}
   const id=i.options.getString('id'); const order=db.prepare('SELECT * FROM orders WHERE id=?').get(id); if(!order)return i.reply({content:'Pedido não encontrado.',ephemeral:true});
   const status=i.commandName==='pedido-aprovar'?'approved':'rejected'; db.prepare('UPDATE orders SET status=? WHERE id=?').run(status,id); const user=await client.users.fetch(order.user_id); await user.send(status==='approved'?`✅ Pedido ${id} aprovado! Entrega será feita em seguida.`:`❌ Pedido ${id} recusado. Fale com a equipe.`).catch(()=>{}); return i.reply({content:`Pedido ${id}: ${status}`,ephemeral:true});
  }
  if(i.isStringSelectMenu()&&i.customId==='add_product'){const pid=Number(i.values[0]);const p=db.prepare('SELECT * FROM products WHERE id=?').get(pid);const cart=carts.get(i.user.id)||[];cart.push(pid);carts.set(i.user.id,cart);return i.reply({content:`✅ ${p.name} adicionado. Use **Ver carrinho** para finalizar.`,ephemeral:true});}
  if(i.isButton()&&i.customId==='view_cart'){const ids=carts.get(i.user.id)||[];if(!ids.length)return i.reply({content:'Seu carrinho está vazio.',ephemeral:true});const items=ids.map(id=>db.prepare('SELECT * FROM products WHERE id=?').get(id));const total=items.reduce((s,p)=>s+p.price,0);const id=`PED-${Date.now().toString(36).toUpperCase()}`;db.prepare('INSERT INTO orders(id,user_id,channel_id,status,total,items) VALUES(?,?,?,?,?,?)').run(id,i.user.id,i.channelId,'awaiting_payment',total,JSON.stringify(ids));carts.delete(i.user.id);const payload=`00020126${String(process.env.PIX_KEY).length}${process.env.PIX_KEY}520400005303986540${(total/100).toFixed(2)}5802BR59${process.env.PIX_RECEIVER}`;const qr=await QRCode.toDataURL(payload);return i.reply({content:`**Pedido ${id}**\nItens: ${items.map(p=>p.name).join(', ')}\nTotal: **${brl(total)}**\n\nPIX: \`${process.env.PIX_KEY}\`\nApós pagar, envie o comprovante neste canal e aguarde a conferência da equipe.`,files:[{attachment:Buffer.from(qr.split(',')[1],'base64'),name:`${id}.png`}],ephemeral:true});}
 } catch(e){console.error(e);if(!i.replied)await i.reply({content:'Erro interno. Tente novamente.',ephemeral:true});}
});
client.once(Events.ClientReady, c=>console.log(`Online como ${c.user.tag}`));
client.login(process.env.DISCORD_TOKEN);
const app=express();app.get('/health',(_,res)=>res.json({ok:true}));app.listen(process.env.PORT||3000,()=>console.log('Health server online'));
