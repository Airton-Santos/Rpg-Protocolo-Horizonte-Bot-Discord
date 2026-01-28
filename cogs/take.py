import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas

class AdminTake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="take", description="[ADMIN] Remove um item do inventário de um jogador")
    @app_commands.describe(
        alvo="O membro que terá o item removido",
        quantidade="Quantidade a ser subtraída",
        nome_item="O nome do item exatamente como consta na mochila"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def tirar_item(self, interaction: discord.Interaction, alvo: discord.Member, quantidade: int, nome_item: str):
        uid = str(alvo.id)
        
        # 1. Carrega do Supabase via db_manager
        fichas = carregar_fichas()

        if uid not in fichas:
            return await interaction.response.send_message(f"❌ {alvo.display_name} não possui um registro bio-sinergia.", ephemeral=True)

        ficha = fichas[uid]
        if "inventario" not in ficha:
            ficha["inventario"] = {}
        
        inventario = ficha["inventario"]
        
        # Normalização para busca
        nome_formatado = nome_item.strip().title()

        # 2. Verifica se o player tem o item
        if nome_formatado not in inventario:
            return await interaction.response.send_message(f"❌ O item **{nome_formatado}** não foi localizado na mochila de {alvo.display_name}.", ephemeral=True)

        if quantidade <= 0:
            return await interaction.response.send_message("❌ A quantidade deve ser maior que zero!", ephemeral=True)

        # 3. Lógica de subtração
        remocao_total = False
        quantidade_atual = inventario[nome_formatado]

        if quantidade >= quantidade_atual:
            del inventario[nome_formatado]
            remocao_total = True
        else:
            inventario[nome_formatado] -= quantidade

        # 4. Salva no Supabase
        try:
            salvar_fichas({uid: ficha})

            embed = discord.Embed(
                title="🗑️ Confisco de Carga",
                description=f"O sistema processou uma remoção de itens.",
                color=0xe74c3c # Vermelho para remoção
            )
            
            if remocao_total:
                embed.add_field(name="Status:", value=f"Todos os exemplares de **{nome_formatado}** foram removidos de {alvo.mention}.")
            else:
                embed.add_field(name="Removido:", value=f"`{quantidade}x {nome_formatado}`", inline=True)
                embed.add_field(name="Restante:", value=f"`{inventario[nome_formatado]}x`", inline=True)
                embed.set_author(name=f"Alvo: {alvo.display_name}")

            embed.set_footer(text="Projeto Fenix | Protocolo de Segurança")
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro crítico ao atualizar banco de dados: {e}", ephemeral=True)

    # Tratamento de erro de permissão
    @tirar_item.error
    async def take_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Acesso negado. Apenas administradores podem confiscar itens.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminTake(bot))