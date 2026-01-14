import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas, carregar_itens, salvar_itens

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="give")
    @commands.has_permissions(administrator=True)
    async def give_item(self, ctx, alvo: discord.Member, quantidade: int, *, nome_item: str):
        uid = str(alvo.id)
        fichas = carregar_fichas()

        if uid not in fichas:
            return await ctx.send(f"❌ {alvo.display_name} não tem uma ficha!")

        if quantidade <= 0:
            return await ctx.send("❌ A quantidade deve ser positiva!")

        # 1. Gerenciar o Catálogo Global (items.json) usando seu db_manager
        itens_globais = carregar_itens()
        foi_novo = False
        
        if nome_item not in itens_globais:
            itens_globais[nome_item] = {} # Apenas registra a existência
            salvar_itens(itens_globais)
            foi_novo = True
        
        # 2. Garantir que o inventário do player existe
        if "inventario" not in fichas[uid]:
            fichas[uid]["inventario"] = {}

        # 3. Adicionar ao inventário do player
        inventario = fichas[uid]["inventario"]
        inventario[nome_item] = inventario.get(nome_item, 0) + quantidade

        salvar_fichas(fichas)

        # Resposta visual
        status_msg = " ✨ (Novo item catalogado!)" if foi_novo else ""
        await ctx.send(f"📦 **{quantidade}x {nome_item}** entregue para **{alvo.display_name}**{status_msg}")

async def setup(bot):
    await bot.add_cog(Admin(bot))