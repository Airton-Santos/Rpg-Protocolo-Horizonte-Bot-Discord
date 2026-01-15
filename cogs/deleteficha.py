import discord
from discord.ext import commands
from utils.db_manager import deletar_fichas

class AdminDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="delete_ficha", aliases=["resetar_ficha"])
    @commands.has_permissions(administrator=True)
    async def remover_ficha_cmd(self, ctx, alvo: discord.Member):
        """Deleta permanentemente a ficha de um jogador."""
        
        # Botão de confirmação para evitar acidentes
        view = ConfirmacaoDelete(alvo)
        await ctx.send(
            f"⚠️ **ALERTA DE SEGURANÇA:**\nVocê está prestes a eliminar o registro biométrico de {alvo.mention}.\n"
            "Isso apagará permanentemente itens, atributos e histórico do banco de dados.\n"
            "**Deseja prosseguir?**", 
            view=view
        )

# Interface de Confirmação
class ConfirmacaoDelete(discord.ui.View):
    def __init__(self, alvo):
        super().__init__(timeout=30)
        self.alvo = alvo

    @discord.ui.button(label="CONFIRMAR EXCLUSÃO", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Apenas ADMs podem clicar no botão de confirmação
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Acesso negado. Apenas administradores podem executar esta ação.", ephemeral=True)

        # Importante: O ID deve ser String para bater com o Supabase
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
        await interaction.response.edit_message(content="❌ Operação abortada. Nenhum dado foi alterado.", view=None)

async def setup(bot):
    await bot.add_cog(AdminDelete(bot))