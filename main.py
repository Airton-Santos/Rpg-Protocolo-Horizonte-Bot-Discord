import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# 1. Configuração de Intenções
# Reduzimos as intenções ao necessário para Slash Commands e Membros
intents = discord.Intents.default()
intents.members = True 
# message_content pode ser False agora, economizando recursos do bot
intents.message_content = False 

# 2. Inicialização do Bot
# Usamos um prefixo nulo/inválido já que o foco é apenas nos comandos "/"
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

# 3. Carregamento Automático de Cogs
async def load_extensions():
    print('--- 📂 CARREGANDO PROTOCOLOS FENIX ---')
    if os.path.exists('./cogs'):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Módulo carregado: {filename}')
                except Exception as e:
                    print(f'❌ Erro ao carregar {filename}: {e}')
    else:
        print("⚠️ Pasta ./cogs não encontrada!")

# 4. Evento: Bot Online e Sincronização
@bot.event
async def on_ready():
    print(f'\n--- 🟢 SISTEMA FENIX ONLINE ---')
    print(f'Identificado como: {bot.user.name}')
    
    try:
        print("🔄 Sincronizando comandos de barra globais...")
        # Sincroniza os comandos "/" com a API do Discord
        synced = await bot.tree.sync()
        print(f"✅ Protocolo atualizado: {len(synced)} comandos ativos!")
    except Exception as e:
        print(f"❌ Falha na sincronização neural: {e}")
    
    # Status visual do bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="Vitória de Santo Antão 2030"
        )
    )
    print(f'--- Feni está pronto para operar ---\n')

# 5. Ponto de Entrada Principal
async def main():
    async with bot:
        await load_extensions()
        
        token_servidor = os.getenv("TOKEN")
        
        if token_servidor:
            await bot.start(token_servidor)
        else:
            print("❌ ERRO CRÍTICO: TOKEN não localizado!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Sistema encerrado. Conexão perdida com 2030...")
    except Exception as e:
        print(f"\n☢️ Erro no núcleo: {e}")