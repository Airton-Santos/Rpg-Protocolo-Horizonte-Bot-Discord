import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import deletar_fichas

class ConfirmacaoDelete(discord.ui.View):
    def __init__(self, alvo, admin):
        super().__init__(timeout=30)
        self.alvo = alvo
        self.admin = admin

    @discord.ui.button(label="CONFIRMAR EXCLUSÃO", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.admin.id:
            return await interaction.response.send_message("❌ Esta confirmação pertence a outro administrador.", ephemeral=True)

        sucesso = deletar_fichas(str(self.alvo.id))
        
        if sucesso:
            await interaction.response.edit_message(
                content=f"✅ **Protocolo de Exclusão Concluído.**\nO registro de {self.alvo.mention} foi expurgado do sistema.", 
                view=None
            )
        else:
            await interaction.response.edit_message(
                content="❌ **Erro:** Registro não encontrado ou já deletado.", 
                view=None
            )

    @discord.ui.button(label="CANCELAR", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.admin.id:
            return await interaction.response.send_message("❌ Ação negada.", ephemeral=True)
            
        await interaction.response.edit_message(content="❌ Operação abortada.", view=None)

class AdminDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # MUDANÇA AQUI: O nome agora é apenas 'delete'
    @app_commands.command(name="delete", description="[ADMIN] Deleta permanentemente a ficha de um jogador")
    @app_commands.describe(alvo="Selecione o cidadão para apagar o registro")
    @app_commands.checks.has_permissions(administrator=True)
    async def remover_ficha_cmd(self, interaction: discord.Interaction, alvo: discord.Member):
        """Interface de exclusão simplificada"""
        
        view = ConfirmacaoDelete(alvo, interaction.user)
        
        await interaction.response.send_message(
            f"⚠️ **ALERTA DE SEGURANÇA:**\nVocê está prestes a eliminar o registro biométrico de {alvo.mention}.\n"
            "Esta ação é irreversível no banco de dados do **Projeto Fenix**.", 
            view=view
        )

    @remover_ficha_cmd.error
    async def delete_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Acesso negado. Apenas administradores.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminDelete(bot))