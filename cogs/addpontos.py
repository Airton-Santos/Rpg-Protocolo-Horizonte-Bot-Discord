import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas # Importamos o salvamento do banco

class AddPontos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addpontos")
    @commands.has_permissions(administrator=True)
    async def adicionar_pontos(self, ctx, alvo: discord.Member, quantidade: int):
        # 1. Carrega as fichas do Supabase
        fichas = carregar_fichas()
        uid = str(alvo.id)

        if uid not in fichas:
            return await ctx.send(f"❌ O usuário {alvo.mention} não possui um registro biométrico no sistema.")
        
        # 2. Atualiza os pontos na memória do bot
        # Usamos .get() por segurança para evitar erros caso a chave 'pontos' não exista
        pontos_atuais = fichas[uid]["informacoes"].get("pontos", 0)
        fichas[uid]["informacoes"]["pontos"] = pontos_atuais + quantidade

        # 3. Salva a alteração no Supabase (apenas a ficha do alvo)
        try:
            salvar_fichas({uid: fichas[uid]})
            
            embed = discord.Embed(
                title="📈 Upgrade de Sistema",
                description=f"O usuário {alvo.mention} recebeu novos pontos de evolução.",
                color=0x3498db
            )
            embed.add_field(name="Quantidade:", value=f"`{quantidade}`", inline=True)
            embed.add_field(name="Novo Total:", value=f"`{fichas[uid]['informacoes']['pontos']}`", inline=True)
            embed.set_footer(text="Protocolo Fenix | Vitória de Santo Antão 2030")
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erro ao salvar no banco de dados: {e}")

async def setup(bot):
    await bot.add_cog(AddPontos(bot))