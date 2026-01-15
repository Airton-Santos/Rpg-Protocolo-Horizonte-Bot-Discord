import discord
from discord.ext import commands

class Utilitarios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ajuda", aliases=["comandos"])
    async def comandos_lista(self, ctx):
        embed = discord.Embed(
            title="📟 Terminal Bio-Sinergia | Protocolo Horizonte",
            description="Interface de comando centralizada. Vitória de Santo Antão, 2030.",
            color=0x3498db
        )

        # --- COMANDOS DE JOGADOR ---
        embed.add_field(
            name="👤 Identidade e Status",
            value=(
                "`!criar` - Inicia a criação da sua ficha.\n"
                "`!status` - Exibe seus atributos e informações.\n"
                "`!profissao` - Escolhe seu estágio e ganha bônus.\n"
                "`!mochila` - Verifica seu inventário atual.\n"
                "`!conhecimentos` - Lista suas perícias aprendidas."
            ),
            inline=False
        )

        embed.add_field(
            name="⚙️ Evolução e Customização",
            value=(
                "`!distribuir` - Painel para gastar pontos de atributos.\n"
                "`!caracteristicas` - Menu de Vantagens e Desvantagens."
            ),
            inline=False
        )

        embed.add_field(
            name="🎲 Ações e Dados (D20 + Modificadores)",
            value=(
                "`!tfor` (Força) | `!tdex` (Destreza)\n"
                "`!tvig` (Vigor) | `!tper` (Percepção)\n"
                "`!tint` (Inteligência) | `!tcar` (Carisma)"
            ),
            inline=False
        )

        # --- COMANDOS DE MESTRE (ADMIN) ---
        if ctx.author.guild_permissions.administrator:
            embed.add_field(
                name="🛠️ Administração (Mestre)",
                value=(
                    "`!addpontos @user qtd` - Dá pontos de evolução.\n"
                    "`!give @user qtd item` - Adiciona item ao inventário.\n"
                    "`!take @user qtd item` - Remove item do inventário.\n"
                    "`!delete_ficha @user` - Apaga permanentemente a ficha."
                ),
                inline=False
            )

        embed.set_footer(text="Conexão Estável | Protocolo Fenix v2.0")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilitarios(bot))