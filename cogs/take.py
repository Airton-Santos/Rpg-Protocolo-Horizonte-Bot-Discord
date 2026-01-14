import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas

class AdminTake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="take")
    @commands.has_permissions(administrator=True)
    async def tirar_item(self, ctx, alvo: discord.Member, quantidade: int, *, nome_item: str):
        uid = str(alvo.id)
        fichas = carregar_fichas()

        # 1. Verifica se o player existe no sistema
        if uid not in fichas:
            return await ctx.send(f"❌ {alvo.display_name} não tem uma ficha.")

        inventario = fichas[uid].get("inventario", {})

        # 2. Verifica se o player realmente tem esse item na mochila
        if nome_item not in inventario:
            return await ctx.send(f"❌ O item **{nome_item}** não está na mochila de {alvo.display_name}.")

        # 3. Lógica de subtração
        if quantidade >= inventario[nome_item]:
            # Se tirar mais ou igual ao que ele tem, remove o item da lista
            del inventario[nome_item]
            await ctx.send(f"🗑️ **{alvo.display_name}** não possui mais **{nome_item}** no inventário.")
        else:
            # Subtrai a quantidade
            inventario[nome_item] -= quantidade
            await ctx.send(f"📉 Removidos **{quantidade}x {nome_item}** de **{alvo.display_name}**. Restam: `{inventario[nome_item]}`")

        # 4. Salva apenas a alteração na ficha do player
        fichas[uid]["inventario"] = inventario
        salvar_fichas(fichas)

async def setup(bot):
    await bot.add_cog(AdminTake(bot))