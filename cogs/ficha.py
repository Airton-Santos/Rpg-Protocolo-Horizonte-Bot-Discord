import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas

class Ficha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="criar")
    @commands.guild_only()
    async def criar_ficha(self, ctx, nome: str, idade: int):
        todas_fichas = carregar_fichas()
        usuario_id = str(ctx.author.id)

        todas_fichas[usuario_id] = {
            "informacoes": {
                "nome": nome,
                "idade": idade,
                "pontos": 25,
                "pontos_caract": 0,
                "profissao": "Nenhuma",
            },
            "status": {
                "forca": 0, "destreza": 0, "inteligencia": 0,
                "vigor": 0, "percepcao": 0, "carisma": 0
            },
            "vantagens": [],
            "desvantagens": []
        }

        salvar_fichas(todas_fichas)
        await ctx.send(f"✅ Ficha de **{nome}** criada com sucesso!")

async def setup(bot):
    await bot.add_cog(Ficha(bot))