import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_itens

# Mudamos o nome da classe aqui para não dar conflito
class CatalogoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Função do Autocomplete
    async def item_autocomplete(self, interaction: discord.Interaction, current: str):
        itens_globais = carregar_itens()
        return [
            app_commands.Choice(name=item, value=item)
            for item in itens_globais.keys() 
            if current.lower() in item.lower()
        ][:25]

    @app_commands.command(name="catalogo", description="Pesquise itens no catálogo global")
    @app_commands.autocomplete(item=item_autocomplete)
    async def catalogo(self, interaction: discord.Interaction, item: str = None):
        itens_globais = carregar_itens()
        
        if not itens_globais:
            return await interaction.response.send_message("📭 Catálogo vazio.", ephemeral=True)

        if item:
            if item in itens_globais:
                embed = discord.Embed(title=f"📦 Item: {item}", color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"❌ Item `{item}` não encontrado.", ephemeral=True)
        else:
            # Lista simples se não pesquisar nada
            lista = sorted(itens_globais.keys())[:30]
            embed = discord.Embed(title="📖 Catálogo Global", description="\n".join(lista), color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)

# No setup, também usamos o novo nome da classe
async def setup(bot):
    await bot.add_cog(CatalogoCog(bot))