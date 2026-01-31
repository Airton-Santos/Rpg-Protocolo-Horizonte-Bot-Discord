import discord
from discord import app_commands
from discord.ext import commands
import os

class Mapas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Caminho absoluto para evitar erros de diretório
        self.caminho_base = os.path.join(os.getcwd(), "assets", "mapas", "cidades")
                
        # Mapeamento de chaves para os nomes reais dos arquivos no seu computador
        self.arquivos_mapas = {
            "bastiao": "bastiao_do_ferro.png",
            "horizonte": "cidadela_horizonte.png",
            "entulho": "entulho_central.png",
            "hope": "new_hope.png"
        }

    @app_commands.command(name="map", description="[ADMIN] Exibe o mapa local da cidade")
    @app_commands.describe(cidade="Qual setor geográfico deseja visualizar?")
    @app_commands.choices(cidade=[
        app_commands.Choice(name="Bastião do Ferro", value="bastiao"),
        app_commands.Choice(name="Cidadela Horizonte", value="horizonte"),
        app_commands.Choice(name="Entulho Central", value="entulho"),
        app_commands.Choice(name="New Hope", value="hope")
    ])
    async def mostrar_mapa(self, interaction: discord.Interaction, cidade: app_commands.Choice[str]):
        # 1. Trava de Segurança: Só Admins
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ **ACESSO NEGADO.**\nSeus privilégios atuais não permitem acesso à cartografia militar.", 
                ephemeral=True
            )

        await interaction.response.defer() # Evita timeout

        # Busca o nome do arquivo usando o value escolhido no menu
        nome_arquivo = self.arquivos_mapas.get(cidade.value)
        caminho_completo = os.path.join(self.caminho_base, nome_arquivo)

        # 2. Verifica se o arquivo realmente existe
        if not os.path.exists(caminho_completo):
            return await interaction.followup.send(
                f"⚠️ Erro: O arquivo `{nome_arquivo}` não foi encontrado em `{self.caminho_base}`.", 
                ephemeral=True
            )

        try:
            # 3. Preparando o arquivo para upload
            file = discord.File(caminho_completo, filename=nome_arquivo)
            
            embed = discord.Embed(
                title=f"🗺️ Setor Identificado: {cidade.name}",
                description=f"Carregando dados cartográficos de {cidade.name} para o Senhor Airton.",
                color=0x3498db
            )
            # Link do anexo para aparecer dentro do embed
            embed.set_image(url=f"attachment://{nome_arquivo}")
            embed.set_footer(text="Sistema de Vigilância Fenix v2.0")

            await interaction.followup.send(file=file, embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Falha crítica ao carregar mapa: {e}")

async def setup(bot):
    await bot.add_cog(Mapas(bot))