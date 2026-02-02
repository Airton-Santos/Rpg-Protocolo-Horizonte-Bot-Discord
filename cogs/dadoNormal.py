import discord
from discord import app_commands
from discord.ext import commands
import random
import re

class Utilidades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dado", description="Lança dados (Ex: 1d20, 2d10, 1d100)")
    @app_commands.describe(formula="A quantidade e o tipo de dado (ex: 1d20)")
    async def lancar_dado(self, interaction: discord.Interaction, formula: str):
        # Usamos Regex para separar o "1" do "20" na string "1d20"
        match = re.fullmatch(r"(\d+)d(\d+)", formula.lower().strip())
        
        if not match:
            return await interaction.response.send_message(
                "❌ Formato inválido! Use algo como `1d20` ou `2d100`.", ephemeral=True
            )

        quantidade = int(match.group(1))
        lados = int(match.group(2))

        # Limite de segurança para não travar o bot
        if quantidade > 100:
            return await interaction.response.send_message("❌ Calma lá! O limite é de 100 dados por vez.", ephemeral=True)

        resultados = [random.randint(1, lados) for _ in range(quantidade)]
        total = sum(resultados)

        # Formatação da mensagem
        embed = discord.Embed(
            title=f"🎲 Lançamento: {formula}",
            color=0x9b59b6
        )
        
        # Se for apenas 1 dado, mostra o resultado direto. Se forem vários, mostra a lista.
        if quantidade == 1:
            res_final = f"🔢 Resultado: **{total}**"
        else:
            res_final = f"📊 Resultados: `{resultados}`\n💰 Total: **{total}**"

        embed.description = res_final
        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilidades(bot))