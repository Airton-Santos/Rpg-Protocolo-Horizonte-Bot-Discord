import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import alternar_apocalipse # Certifique-se que essa função está no seu db_manager

class AdminRPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setapocalipse", description="[ADMIN] Define se o estado do mundo é Apocalipse (True) ou Normal (False)")
    @app_commands.describe(status="True para ATIVAR o apocalipse, False para DESATIVAR")
    async def setapocalipse(self, interaction: discord.Interaction, status: bool):
        # Segurança: Apenas Administradores (Senhor Airton)
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Acesso negado. Apenas o mestre pode alterar o destino de Vitória.", ephemeral=True)

        await interaction.response.defer()

        try:
            # Atualiza o status no Supabase
            sucesso = alternar_apocalipse(status)

            if sucesso:
                if status:
                    embed = discord.Embed(
                        title="⚠️ PROTOCOLO FENIX ATIVADO",
                        description="**O Apocalipse começou.**\nStatus: `TRUE`\nO sistema global agora opera em modo de Sobrevivência Brutal.",
                        color=0xff0000
                    )
                else:
                    embed = discord.Embed(
                        title="🌐 PROTOCOLO FENIX EM STANDBY",
                        description="**O Mundo retornou à normalidade.**\nStatus: `FALSE`\nO sistema global retornou ao modo de Investigação.",
                        color=0x00ff00
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Erro ao comunicar com o núcleo do Supabase.")

        except Exception as e:
            await interaction.followup.send(f"❌ Erro ao executar comando: {e}")

async def setup(bot):
    await bot.add_cog(AdminRPG(bot))