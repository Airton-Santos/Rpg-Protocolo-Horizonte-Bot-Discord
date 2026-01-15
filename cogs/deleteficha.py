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
        
        # Criando um botão de confirmação para evitar deletar sem querer
        view = ConfirmacaoDelete(alvo)
        await ctx.send(f"⚠️ **CUIDADO:** Você está prestes a deletar a ficha de {alvo.mention}. Isso apagará itens, atributos e história. Confirmar?", view=view)

# Interface de Confirmação (Botão)
class ConfirmacaoDelete(discord.ui.View):
    def __init__(self, alvo):
        super().__init__(timeout=30)
        self.alvo = alvo

    @discord.ui.button(label="DELETAR TUDO", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Só ADMs podem confirmar isso.", ephemeral=True)

        sucesso = deletar_fichas(self.alvo.id)
        
        if sucesso:
            await interaction.response.edit_message(content=f"✅ A ficha de **{self.alvo.display_name}** foi eliminada dos bancos de dados da Bio-Sinergia.", view=None)
        else:
            await interaction.response.edit_message(content="❌ Esse usuário não tinha uma ficha cadastrada.", view=None)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Operação cancelada.", view=None)

async def setup(bot):
    await bot.add_cog(AdminDelete(bot))