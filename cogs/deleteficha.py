import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import deletar_fichas

# Interface de Confirmação (Botões)
class ConfirmacaoDelete(discord.ui.View):
    def __init__(self, alvo, admin):
        super().__init__(timeout=30)
        self.alvo = alvo
        self.admin = admin

    @discord.ui.button(label="CONFIRMAR EXCLUSÃO", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Garante que apenas QUEM CHAMOU o comando pode clicar no botão
        if interaction.user.id != self.admin.id:
            return await interaction.response.send_message("❌ Esta confirmação pertence a outro administrador.", ephemeral=True)

        sucesso = deletar_fichas(str(self.alvo.id))
        
        if sucesso:
            await interaction.response.edit_message(
                content=f"✅ **Protocolo de Exclusão Concluído.**\nA ficha de **{self.alvo.display_name}** foi removida do sistema central.", 
                view=None
            )
        else:
            await interaction.response.edit_message(
                content="❌ **Erro:** Registro não encontrado no banco de dados.", 
                view=None
            )

    @discord.ui.button(label="CANCELAR", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.admin.id:
            return await interaction.response.send_message("❌ Ação negada.", ephemeral=True)
            
        await interaction.response.edit_message(content="❌ Operação abortada. Nenhum dado foi alterado.", view=None)

class AdminDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="delete_ficha", description="[ADMIN] Deleta permanentemente a ficha de um jogador")
    @app_commands.describe(alvo="Jogador que terá o registro biométrico apagado")
    @app_commands.checks.has_permissions(administrator=True)
    async def remover_ficha_cmd(self, interaction: discord.Interaction, alvo: discord.Member):
        """Interface de exclusão de fichas via Slash Command"""
        
        view = ConfirmacaoDelete(alvo, interaction.user)
        
        await interaction.response.send_message(
            f"⚠️ **ALERTA DE SEGURANÇA:**\nVocê está prestes a eliminar o registro biométrico de {alvo.mention}.\n"
            "Isso apagará permanentemente itens, atributos e histórico do banco de dados.\n"
            "**Deseja prosseguir?**", 
            view=view
        )

    # Tratamento de erro de permissão
    @remover_ficha_cmd.error
    async def delete_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Acesso negado. Comando restrito a administradores.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminDelete(bot))