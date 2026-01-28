import discord
from discord import app_commands
from discord.ext import commands

class Utilitarios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ajuda", description="Exibe a lista de comandos do Protocolo Horizonte")
    async def ajuda(self, interaction: discord.Interaction):
        # Aqui usamos interaction.user para checar permissões
        is_admin = interaction.user.guild_permissions.administrator

        embed = discord.Embed(
            title="📟 Terminal Bio-Sinergia | Protocolo Horizonte",
            description="Interface de comando centralizada. Vitória de Santo Antão, 2030.",
            color=0x3498db
        )

        # --- COMANDOS DE JOGADOR ---
        embed.add_field(
            name="👤 Identidade e Status",
            value=(
                "`/criar` - Inicia a criação da sua ficha.\n"
                "`/perfil` - Exibe suas informações.\n"
                "`/status` - Exibe seus atributos e informações.\n"
                "`/profissao` - Escolhe seu estágio e ganha bônus.\n"
                "`/mochila` - Verifica seu inventário atual.\n"
                "`/catalogo` - Lista itens registrados no sistema."
            ),
            inline=False
        )

        embed.add_field(
            name="⚙️ Evolução e Customização",
            value=(
                "`/distribuir` - Painel para gastar pontos de atributos.\n"
                "`/caracteristicas` - Menu de Vantagens e Desvantagens."
            ),
            inline=False
        )

        embed.add_field(
            name="🎲 Ações e Dados (D20 + Modificadores)",
            value=(
                "`/tfor` (Força) | `/tdex` (Destreza)\n"
                "`/tvig` (Vigor) | `/tper` (Percepção)\n"
                "`/tint` (Inteligência) | `/tcar` (Carisma)"
            ),
            inline=False
        )

        # --- COMANDOS DE MESTRE (ADMIN) ---
        if is_admin:
            embed.add_field(
                name="🛠️ Administração (Mestre)",
                value=(
                    "`/addpontos` - Dá pontos de evolução.\n"
                    "`/give` - Adiciona item ao inventário.\n"
                    "`/take` - Remove item do inventário.\n"
                    "`/delete_ficha` - Apaga permanentemente a ficha."
                ),
                inline=False
            )

        embed.set_footer(text="Conexão Estável | Protocolo Fenix v2.6")
        
        # Enviamos a resposta (ephemeral=True para não poluir o chat dos outros, se preferir)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilitarios(bot))