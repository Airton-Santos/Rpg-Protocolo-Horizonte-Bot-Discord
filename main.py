import discord
from discord.ext import commands
import os
import asyncio

# 1. Configuração de Intenções
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia o conteúdo das mensagens
intents.members = True          # Permite que o bot veja quem entrou no servidor

# 2. Inicialização do Bot usando Variáveis de Ambiente (Railway)
# Se não encontrar a variável PREFIXO, ele usará "!" por padrão
prefixo_do_sistema = os.getenv("PREFIXO", "!")
bot = commands.Bot(command_prefix=prefixo_do_sistema, intents=intents)

# 3. Carregamento Automático de Cogs
async def load_extensions():
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Módulo carregado: {filename}')
                except Exception as e:
                    print(f'❌ Erro ao carregar {filename}: {e}')
    else:
        print("⚠️ Pasta ./cogs não encontrada no servidor!")

# 4. Evento: Bot Online
@bot.event
async def on_ready():
    print(f'\n--- 🟢 SISTEMA FENIX ONLINE ---')
    print(f'Identidade: {bot.user.name}')
    print(f'Prefixo: {prefixo_do_sistema}')
    print(f'--- Protocolo Horizonte 2030 ---\n')

# 5. Ponto de Entrada Principal
async def main():
    async with bot:
        await load_extensions()
        
        # Puxa o TOKEN das variáveis que você configurou no painel do Railway
        token_servidor = os.getenv("TOKEN")
        
        if token_servidor:
            await bot.start(token_servidor)
        else:
            print("❌ ERRO: Variável 'TOKEN' não encontrada nas configurações do Railway!")

# Rodar o projeto
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Saindo...")