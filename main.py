import discord
from discord.ext import commands
import os
import config # Importa o seu arquivo config.py


intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia o conteúdo das mensagens
intents.members = True          # Permite que o bot veja quem entrou no servidor


bot = commands.Bot(command_prefix=config.PREFIXO, intents=intents)


# Em vez de escrever tudo aqui, o bot vai na pasta /cogs e lê os arquivos .py
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'): # Verifica se o arquivo é um módulo Python
            # Isso transforma 'ficha.py' em 'cogs.ficha' e carrega no bot
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Módulo carregado: {filename}')


# Roda uma única vez quando o bot consegue se conectar ao Discord
@bot.event
async def on_ready():
    print(f'--- Gerenciador {bot.user.name} online! ---')
    print(f'ID do Bot: {bot.user.id}')

# O ponto de entrada que inicia o processo assíncrono
async def main():
    async with bot:
        await load_extensions() # Primeiro carrega os módulos
        await bot.start(config.TOKEN) # Depois liga o bot com o Token

# Rodar o projeto
import asyncio
if __name__ == "__main__":
    asyncio.run(main())