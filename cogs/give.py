import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas, carregar_itens, salvar_itens

class AdminItens(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="give", description="[ADMIN] Entrega um item para o inventário de um jogador")
    @app_commands.describe(
        alvo="O membro que receberá o item",
        quantidade="Quantos itens entregar",
        nome_item="O nome do item (ex: Pistola 9mm)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def give_item(self, interaction: discord.Interaction, alvo: discord.Member, quantidade: int, nome_item: str):
        uid = str(alvo.id)
        
        # 1. Carregar as fichas
        fichas = carregar_fichas()

        if uid not in fichas:
            return await interaction.response.send_message(
                f"❌ {alvo.display_name} não possui um registro biométrico!", 
                ephemeral=True
            )

        if quantidade <= 0:
            return await interaction.response.send_message(
                "❌ A quantidade deve ser superior a zero!", 
                ephemeral=True
            )

        # 2. Gerenciar o Catálogo Global
        itens_globais = carregar_itens()
        foi_novo = False
        
        # Normalizando o nome para evitar "Item" e "item" como duplicados
        nome_item_formatado = nome_item.strip().title()
        
        if nome_item_formatado not in itens_globais:
            itens_globais[nome_item_formatado] = {} 
            salvar_itens(itens_globais)
            foi_novo = True
        
        # 3. Atualizar Inventário do Player
        if "inventario" not in fichas[uid]:
            fichas[uid]["inventario"] = {}

        inventario = fichas[uid]["inventario"]
        inventario[nome_item_formatado] = inventario.get(nome_item_formatado, 0) + quantidade

        # 4. Salvar no Supabase
        try:
            salvar_fichas({uid: fichas[uid]})
            
            status_msg = " ✨ (Novo item catalogado no Protocolo!)" if foi_novo else ""
            
            embed = discord.Embed(
                title="📦 Entrega de Suprimentos",
                description=f"O sistema processou uma transferência de carga.",
                color=0x2ecc71
            )
            embed.add_field(name="Destinatário:", value=alvo.mention, inline=True)
            embed.add_field(name="Item:", value=f"`{quantidade}x {nome_item_formatado}`", inline=True)
            if foi_novo:
                embed.set_footer(text=f"Aviso: {nome_item_formatado} foi adicionado ao catálogo global.")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao sincronizar com o banco: {e}", ephemeral=True)

    # Erro de permissão
    @give_item.error
    async def give_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Apenas administradores podem usar o protocolo de suprimentos.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminItens(bot))