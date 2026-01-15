import discord
from discord.ext import commands
# Importamos as funções que conversam com o Supabase
from utils.db_manager import carregar_fichas, salvar_fichas, carregar_itens, salvar_itens

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="give")
    @commands.has_permissions(administrator=True)
    async def give_item(self, ctx, alvo: discord.Member, quantidade: int, *, nome_item: str):
        uid = str(alvo.id)
        
        # 1. Carregar as fichas para encontrar a do alvo
        # (Nota: No futuro, podemos criar 'carregar_uma_ficha' para ser mais rápido)
        fichas = carregar_fichas()

        if uid not in fichas:
            return await ctx.send(f"❌ {alvo.display_name} não tem uma ficha no banco de dados!")

        if quantidade <= 0:
            return await ctx.send("❌ A quantidade deve ser positiva!")

        # 2. Gerenciar o Catálogo Global (Tabela itens_globais no Supabase)
        itens_globais = carregar_itens()
        foi_novo = False
        
        if nome_item not in itens_globais:
            itens_globais[nome_item] = {} # Registra o item no catálogo
            salvar_itens(itens_globais)
            foi_novo = True
        
        # 3. Garantir que o inventário do player existe e adicionar
        if "inventario" not in fichas[uid]:
            fichas[uid]["inventario"] = {}

        inventario = fichas[uid]["inventario"]
        inventario[nome_item] = inventario.get(nome_item, 0) + quantidade

        # 4. SALVAR NO SUPABASE
        # Enviamos apenas a ficha atualizada do alvo para o seu db_manager
        try:
            salvar_fichas({uid: fichas[uid]})
            
            # Resposta visual
            status_msg = " ✨ (Item catalogado no sistema!)" if foi_novo else ""
            await ctx.send(f"📦 **{quantidade}x {nome_item}** entregue para **{alvo.display_name}**{status_msg}")
        except Exception as e:
            await ctx.send(f"❌ Erno ao sincronizar com o banco: {e}")

async def setup(bot):
    await bot.add_cog(Admin(bot))