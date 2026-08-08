#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════
  SKYLERS GENPAGO BOT  ·  v1.0
═══════════════════════════════════════════════════════════════════════
  Bot educacional de geração de contas para Discord
  Linguagem : Python 3.8+
  Biblioteca: discord.py (2.x)
  Comandos  : /verificar e /gerar
  Status    : Funcional & Educativo

  ── AVISO LEGAL (leia antes de usar) ────────────────────────────────
  Este bot é um TEMPLATE DE DEMONSTRAÇÃO. Ele gera apenas credenciais
  FICTÍCIAS e aleatórias (ex.: netflix_user1:pass1) para fins
  educacionais, de estudo da biblioteca discord.py e de prototipagem.

  • Nenhuma conta real é criada, roubada ou distribuída;
  • Não use dados de contas reais, listas vazadas ou geradores que
    violem os Termos de Serviço do Discord ou de terceiros;
  • Opere sempre dentro dos ToS da plataforma. A responsabilidade
    pelo uso é de quem opera o bot.

  by Sony Skylers
═══════════════════════════════════════════════════════════════════════
"""

import os
import re
import json
import random
import string
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

# ---------------------------------------------------------------------
# 1. CONFIGURAÇÃO BÁSICA
# ---------------------------------------------------------------------

# Carrega o token do ambiente (recomendado) ou do arquivo .env.
# Nunca coloque o token direto no código!
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv é opcional
    pass

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

# Canal onde o bot pode operar (opcional).
# Deixe vazio ("") para liberar em qualquer canal do servidor.
CANAL_PERMITIDO = os.getenv("CANAL_GENPAGO", "").strip()

# Tempo de espera (em segundos) entre um /gerar e outro, por usuário.
COOLDOWN_SEGUNDOS = int(os.getenv("COOLDOWN_SEGUNDOS", "30"))

# Validade (em horas) de uma conta gerada, usada pelo /verificar.
VALIDADE_HORAS = int(os.getenv("VALIDADE_HORAS", "24"))

# ID de um servidor de testes (opcional): se preenchido, os comandos
# ficam disponíveis na hora nesse servidor, sem esperar o Discord
# propagar comandos globais (que pode levar até 1 hora).
TEST_GUILD_ID = os.getenv("TEST_GUILD_ID", "").strip()

# Arquivo local onde as contas geradas ficam registradas
# (apenas para o /verificar saber o que o próprio bot gerou).
ARQUIVO_DADOS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "contas_geradas.json"
)

# ---------------------------------------------------------------------
# 2. CATÁLOGO DE CATEGORIAS (apenas dados fictícios de demonstração)
# ---------------------------------------------------------------------
# Cada categoria define um "gerador" de nomes de usuário fictícios.
# Os padrões são aleatórios e NÃO correspondem a contas reais.
# ---------------------------------------------------------------------

CATEGORIAS = {
    "netflix": {
        "emoji": "\U0001f37f",  # 🍿
        "nome": "Netflix",
        "usuario": lambda: f"netflix_user{random.randint(100, 999)}",
        "dominio": "mail.com",
    },
    "spotify": {
        "emoji": "\U0001f3b5",  # 🎵
        "nome": "Spotify",
        "usuario": lambda: f"spotify_user{random.randint(100, 999)}",
        "dominio": "mail.com",
    },
    "disney": {
        "emoji": "\U0001f680",  # 🚀
        "nome": "Disney+",
        "usuario": lambda: f"disney_user{random.randint(100, 999)}",
        "dominio": "mail.com",
    },
    "primevideo": {
        "emoji": "\U0001f4fa",  # 📺
        "nome": "Prime Video",
        "usuario": lambda: f"prime_user{random.randint(100, 999)}",
        "dominio": "mail.com",
    },
    "hbomax": {
        "emoji": "\U0001f3ac",  # 🎬
        "nome": "HBO Max",
        "usuario": lambda: f"hbo_user{random.randint(100, 999)}",
        "dominio": "mail.com",
    },
    "crunchyroll": {
        "emoji": "\U0001f3ae",  # 🎮
        "nome": "Crunchyroll",
        "usuario": lambda: f"crunchy_user{random.randint(100, 999)}",
        "dominio": "mail.com",
    },
    "steam": {
        "emoji": "\U0001f3b2",  # 🎲
        "nome": "Steam",
        "usuario": lambda: f"steam_user{random.randint(100, 999)}",
        "dominio": "mail.com",
    },
    "youtube": {
        "emoji": "\U0001f3a5",  # 🎥
        "nome": "YouTube Premium",
        "usuario": lambda: f"yt_user{random.randint(100, 999)}",
        "dominio": "mail.com",
    },
}


def gerar_senha_ficticia(tamanho: int = 10) -> str:
    """Gera uma senha aleatória FICTÍCIA (somente demonstração)."""
    caracteres = string.ascii_letters + string.digits
    return "".join(random.choice(caracteres) for _ in range(tamanho))


def gerar_conta_ficticia(categoria: str) -> dict:
    """Cria um par login:senha fictício para a categoria escolhida."""
    info = CATEGORIAS[categoria]
    usuario = info["usuario"]()
    email = f"{usuario}@{info['dominio']}"
    senha = f"{info['nome'].split()[0].lower()}{random.randint(1000, 9999)}"
    return {"email": email, "senha": senha}


# ---------------------------------------------------------------------
# 3. BANCO DE DADOS LOCAL (registro das contas geradas)
# ---------------------------------------------------------------------

def _carregar_registro() -> dict:
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _salvar_registro(registro: dict) -> None:
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(registro, f, ensure_ascii=False, indent=2)
    except OSError as erro:
        print(f"[aviso] Não foi possível salvar o registro: {erro}")


def registrar_conta(email: str, senha: str, categoria: str, autor_id: int) -> None:
    """Guarda a conta fictícia gerada, para o /verificar consultar."""
    registro = _carregar_registro()
    agora = datetime.now(timezone.utc)
    registro[email] = {
        "senha": senha,
        "categoria": categoria,
        "autor_id": autor_id,
        "criada_em": agora.isoformat(),
        "validade_horas": VALIDADE_HORAS,
    }
    _salvar_registro(registro)


def consultar_conta(email: str) -> dict | None:
    """Procura um e-mail no registro local. Retorna None se não existir."""
    return _carregar_registro().get(email)


# ---------------------------------------------------------------------
# 4. CLIENTE DO BOT
# ---------------------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True  # necessário apenas se for ler mensagens

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,  # desativa o help de prefixo; usamos comandos "/"
)

tree = bot.tree


def embed_padrao(cor: discord.Color, titulo: str, descricao: str) -> discord.Embed:
    """Cria um embed com o visual padrão do bot."""
    return discord.Embed(
        title=titulo,
        description=descricao,
        color=cor,
        timestamp=datetime.now(timezone.utc),
    )


def canal_permitido(interaction: discord.Interaction) -> bool:
    """True se o comando pode rodar no canal atual."""
    if not CANAL_PERMITIDO:
        return True
    canal = interaction.channel
    return canal is not None and (
        str(canal.id) == CANAL_PERMITIDO or str(canal) == CANAL_PERMITIDO
    )


# ---------------------------------------------------------------------
# 5. EVENTOS
# ---------------------------------------------------------------------

@bot.event
async def on_ready():
    print("=" * 56)
    print("  Skylers GenPago Bot online!")
    print(f"  Logado como: {bot.user} (ID: {bot.user.id})")
    print(f"  Servidores  : {len(bot.guilds)}")
    print("=" * 56)
    print("\nConvite rápido (abra no navegador):")
    print(
        "  https://discord.com/oauth2/authorize?client_id="
        f"{bot.user.id}&scope=bot+applications.commands&permissions=2147485696"
    )

    # Sincroniza os comandos "/" com o Discord.
    # Com TEST_GUILD_ID preenchido, ficam disponíveis na hora nesse
    # servidor; sem ele, são globais (podem levar até 1h para aparecer).
    try:
        if TEST_GUILD_ID:
            guild = discord.Object(id=int(TEST_GUILD_ID))
            tree.copy_global_to(guild=guild)
            await tree.sync(guild=guild)
            print(f"\nComandos sincronizados no servidor de teste {TEST_GUILD_ID}.")
        else:
            await tree.sync()
            print("\nComandos globais sincronizados.")
    except Exception as erro:  # noqa: BLE001
        print(f"[aviso] Falha ao sincronizar comandos: {erro}")

    print("\nComandos registrados: /gerar · /verificar")


# ---------------------------------------------------------------------
# 6. COMANDOS
# ---------------------------------------------------------------------

@tree.command(
    name="gerar",
    description="Gera uma conta fictícia de demonstração para a categoria.",
)
@app_commands.checks.cooldown(1, COOLDOWN_SEGUNDOS, key=lambda i: i.user.id)
@app_commands.choices(
    categoria=[
        app_commands.Choice(name=f"{c['emoji']} {c['nome']}", value=slug)
        for slug, c in CATEGORIAS.items()
    ]
)
async def gerar(
    interaction: discord.Interaction,
    categoria: app_commands.Choice[str],
):
    """Comando: /gerar categoria:Netflix
    Gera uma credencial FICTÍCIA e responde com um embed."""
    if not canal_permitido(interaction):
        embed = embed_padrao(
            discord.Color.red(),
            ":no_entry: Canal não permitido",
            f"Use este comando apenas no canal configurado: <#{CANAL_PERMITIDO}>",
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    slug = categoria.value
    info = CATEGORIAS[slug]
    conta = gerar_conta_ficticia(slug)

    # Registra para o /verificar (apenas local, nada é enviado a terceiros)
    registrar_conta(conta["email"], conta["senha"], slug, interaction.user.id)

    credencial = f"{conta['email']}:{conta['senha']}"

    # Embed no formato pedido: título, descrição e dados em spoiler
    embed = discord.Embed(
        title=f":tada: Conta {info['nome']} Gerada!",
        description="Aqui estão os seus dados de acesso:",
        color=discord.Color.green(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(name="dados", value=f"||{credencial}||", inline=False)
    embed.add_field(
        name=":information_source: Aviso",
        value=(
            "Credencial **fictícia** gerada apenas para demonstração. "
            f"Válida por {VALIDADE_HORAS}h no registro do bot "
            "(use `/verificar`)."
        ),
        inline=False,
    )
    embed.set_footer(
        text=f"Skylers GenPago Bot · solicitado por {interaction.user.display_name}"
    )

    await interaction.response.send_message(embed=embed)


@tree.command(
    name="verificar",
    description="Verifica se uma conta foi gerada por este bot.",
)
async def verificar(
    interaction: discord.Interaction,
    email: str,
):
    """Comando: /verificar email:netflix_user123@mail.com
    Confere no registro local se a credencial foi gerada pelo bot."""
    email = email.strip().lower()

    # Validação básica de formato de e-mail
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        embed = embed_padrao(
            discord.Color.orange(),
            ":warning: Formato inválido",
            "Informe um e-mail válido, ex.: `netflix_user123@mail.com`",
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    conta = consultar_conta(email)

    if conta is None:
        embed = embed_padrao(
            discord.Color.red(),
            ":x: Conta não encontrada",
            f"Nenhuma conta gerada por este bot corresponde a `{email}`.",
        )
        embed.add_field(
            name="Dica",
            value="As credenciais geradas são fictícias e ficam registradas "
            "apenas localmente, na máquina que roda o bot.",
            inline=False,
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # Calcula se ainda está dentro da validade
    criada_em = datetime.fromisoformat(conta["criada_em"])
    expira_em = criada_em + timedelta(hours=conta["validade_horas"])
    valida = datetime.now(timezone.utc) < expira_em

    nome_categoria = CATEGORIAS[conta["categoria"]]["nome"]
    cor = discord.Color.green() if valida else discord.Color.red()
    simbolo = ":white_check_mark:" if valida else ":clock1:"

    embed = discord.Embed(
        title=f"{simbolo} Conta {nome_categoria} Verificada",
        description="Resultado da verificação:",
        color=cor,
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(name="dados", value=f"||{email}:{conta['senha']}||", inline=False)
    embed.add_field(name="Categoria", value=nome_categoria, inline=True)
    embed.add_field(
        name="Status",
        value="**Válida** (dentro da validade)" if valida else "**Expirada**",
        inline=True,
    )
    embed.add_field(
        name="Expira em",
        value=discord.utils.format_dt(expira_em, style="R"),
        inline=True,
    )
    embed.set_footer(text="Skylers GenPago Bot · verificação local (demonstração)")

    await interaction.response.send_message(embed=embed)


# ---------------------------------------------------------------------
# 7. TRATAMENTO DE ERROS
# ---------------------------------------------------------------------

@tree.error
async def on_tree_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
):
    if isinstance(error, app_commands.CommandOnCooldown):
        embed = embed_padrao(
            discord.Color.orange(),
            ":hourglass_flowing_sand: Calma aí!",
            f"Aguarde **{error.retry_after:.0f}s** antes de gerar outra conta.",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = embed_padrao(
            discord.Color.red(),
            ":rotating_light: Erro inesperado",
            f"```{error}```",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"[erro] {type(error).__name__}: {error}")


# ---------------------------------------------------------------------
# 8. INICIALIZAÇÃO
# ---------------------------------------------------------------------

if __name__ == "__main__":
    if not TOKEN:
        print(
            "[ERRO] Variável DISCORD_TOKEN não encontrada.\n"
            "Crie um arquivo .env na mesma pasta com:\n"
            "  DISCORD_TOKEN=seu_token_aqui\n"
            "Ou exporte a variável de ambiente antes de rodar."
        )
        raise SystemExit(1)

    bot.run(TOKEN)
