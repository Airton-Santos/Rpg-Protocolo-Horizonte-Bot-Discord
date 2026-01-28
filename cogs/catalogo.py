import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_itens

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 1. LÓGICA DA BARRA DE PESQUISA (AUTOCOMPLETE) ---
    async def item_autocomplete(self, interaction: discord.Interaction, current: str):
        itens_globais = carregar_itens()
        # Filtra os itens conforme você digita (ignora maiúsculas/minúsculas)
        return [
            app_commands.Choice(name=item, value=item)
            for item in itens_globais.keys() 
            if current.lower() in item.lower()
        ][:25] # O Discord limita a 25 sugestões na barra

    # --- 2. O COMANDO DE BARRA ---
    @app_commands.command(name="catalogo", description="Pesquise itens ou veja o catálogo completo do Projeto Fenix")
    @app_commands.autocomplete(item=item_autocomplete)
    async def catalogo(self, interaction: discord.Interaction, item: str = None):
        itens_globais = carregar_itens()
        
        if not itens_globais:
            return await interaction.response.send_message("📭 O catálogo global ainda está vazio.", ephemeral=True)

        # CASO 1: Se o usuário pesquisou/selecionou um item específico
        if item:
            if item in itens_globais:
                embed = discord.Embed(
                    title=f"📦 Item: {item}",
                    description="✅ Este item está registrado no Catálogo Global.",
                    color=discord.Color.green()
                )
                # Se no futuro você adicionar descrições no Supabase, elas entrariam aqui
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"❌ O item `{item}` não foi encontrado.", ephemeral=True)
        
        # CASO 2: Se o usuário apenas deu Enter sem escolher um item (Mostra Tudo)
        else:
            lista_ordenada = sorted(itens_globais.keys())
            total = len(lista_ordenada)
            
            # Pegamos os primeiros 30 para o embed não ficar gigante
            texto_lista = "\n".join([f"• {i}" for i in lista_ordenada[:30]])
            
            embed = discord.Embed(
                title="📖 Catálogo Global de Itens",
                description=texto_lista,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Total: {total} itens | Digite para pesquisar na barra.")
            
            if total > 30:
                embed.description += "\n\n*...e outros. Use a pesquisa para achar itens específicos!*"

            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))