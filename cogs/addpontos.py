import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas

class AddPontos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addpontos", description="[ADMIN] Adiciona pontos de evolução a um usuário")
    @app_commands.describe(alvo="Membro que receberá os pontos", quantidade="Quantidade de pontos a adicionar")
    @app_commands.checks.has_permissions(administrator=True)
    async def adicionar_pontos(self, interaction: discord.Interaction, alvo: discord.Member, quantidade: int):
        # Em Slash Commands, usa-se 'interaction' em vez de 'ctx'
        uid = str(alvo.id)
        fichas = carregar_fichas()

        if uid not in fichas:
            return await interaction.response.send_message(
                f"❌ O usuário {alvo.mention} não possui um registro biométrico no sistema.", 
                ephemeral=True
            )
        
        # 2. Atualiza os pontos
        # Garantindo que a estrutura 'informacoes' existe para evitar erros
        if "informacoes" not in fichas[uid]:
            fichas[uid]["informacoes"] = {}

        pontos_atuais = fichas[uid]["informacoes"].get("pontos", 0)
        fichas[uid]["informacoes"]["pontos"] = pontos_atuais + quantidade

        # 3. Salva no Supabase
        try:
            salvar_fichas({uid: fichas[uid]})
            
            embed = discord.Embed(
                title="📈 Upgrade de Sistema",
                description=f"O usuário {alvo.mention} recebeu novos pontos de evolução.",
                color=0x3498db
            )
            embed.add_field(name="Quantidade:", value=f"`{quantidade}`", inline=True)
            embed.add_field(name="Novo Total:", value=f"`{fichas[uid]['informacoes']['pontos']}`", inline=True)
            embed.set_footer(text="Protocolo Fenix | Vitória 2030")
            
            # Responder à interação
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao salvar no banco de dados: {e}", ephemeral=True)

    # Tratamento de erro caso alguém sem permissão tente usar
    @adicionar_pontos.error
    async def addpontos_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Você não tem permissão de Administrador para usar este comando.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AddPontos(bot))