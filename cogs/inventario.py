import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas

class Inventario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mochila", aliases=["inv", "inventario"])
    async def ver_mochila(self, ctx):
        uid = str(ctx.author.id)
        fichas = carregar_fichas()

        if uid not in fichas:
            return await ctx.send("❌ Você não possui uma ficha criada.")

        ficha = fichas[uid]
        inventario = ficha.get("inventario", {})

        embed = discord.Embed(
            title=f"🎒 Mochila de {ficha['informacoes']['nome']}",
            description="Aqui estão os itens que você carrega em 2030.",
            color=0x2ecc71
        )

        if not inventario:
            embed.description = "Sua mochila está vazia. Explore Vitória de Santo Antão para encontrar itens!"
        else:
            # Lista os itens: "• 5x Bandagem"
            lista_itens = "\n".join([f"• **{qtd}x** {item}" for item, qtd in inventario.items()])
            embed.add_field(name="Conteúdo:", value=lista_itens, inline=False)

        embed.set_footer(text="Protocolo Horizonte | Bio-Sinergia")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventario(bot))