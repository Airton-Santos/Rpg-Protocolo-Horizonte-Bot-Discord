import discord # Para criar as mensagens bonitas (Embeds)
from discord.ext import commands # Para registrar o comando no Bot
import json # Para conseguir ler o seu arquivo requisitos.json
from utils.db_manager import carregar_fichas # Para buscar a ficha do player

class addpontos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command(name="addpontos") #Nome do comando
    @commands.has_permissions(administrator=True) #Comandos só para admins
    async def adicionar_pontos(self, ctx, alvo: discord.Member, quantidade: int):

        fichas = carregar_fichas()
        uid = str(alvo.id)

        if uid not in fichas:
            return await ctx.send("❌ Ficha não encontrada para este usuário!")
        
        fichas[uid]["informacoes"]["pontos"] += quantidade

        with open("database/fichas.json", "w", encoding="utf-8") as f:
            json.dump(fichas, f, indent=4, ensure_ascii=False)
            
            await ctx.send(f"✅ Adicionados {quantidade} pontos ao usuário {alvo.mention}.")
# FORA DA CLASSE (Alinhado à esquerda)
async def setup(bot):
    await bot.add_cog(addpontos(bot))
            

            
            