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
        
        # 1. Carrega do Supabase via db_manager
        fichas = carregar_fichas()

        if uid not in fichas:
            return await ctx.send(f"❌ {alvo.display_name} não possui um registro bio-sinergia.")

        # Acessa a ficha e o inventário de forma segura
        ficha = fichas[uid]
        if "inventario" not in ficha:
            ficha["inventario"] = {}
        
        inventario = ficha["inventario"]

        # 2. Verifica se o player realmente tem esse item na mochila
        # Dica: use .lower() ou strip() se quiser evitar erros de digitação (opcional)
        if nome_item not in inventario:
            return await ctx.send(f"❌ O item **{nome_item}** não consta no inventário de {alvo.display_name}.")

        if quantidade <= 0:
            return await ctx.send("❌ A quantidade a ser removida deve ser maior que zero!")

        # 3. Lógica de subtração
        remocao_total = False
        if quantidade >= inventario[nome_item]:
            # Remove o item completamente
            del inventario[nome_item]
            remocao_total = True
        else:
            # Subtrai a quantidade
            inventario[nome_item] -= quantidade

        # 4. Salva APENAS a ficha do player no Supabase
        try:
            # Enviamos o dicionário {UID: DADOS_ATUALIZADOS}
            salvar_fichas({uid: ficha})

            if remocao_total:
                await ctx.send(f"🗑️ **{alvo.display_name}** teve todos os exemplares de **{nome_item}** removidos.")
            else:
                await ctx.send(f"📉 Removidos **{quantidade}x {nome_item}** de **{alvo.display_name}**. Restam: `{inventario[nome_item]}`")
        
        except Exception as e:
            await ctx.send(f"❌ Erro crítico ao atualizar banco de dados: {e}")

async def setup(bot):
    await bot.add_cog(AdminTake(bot))