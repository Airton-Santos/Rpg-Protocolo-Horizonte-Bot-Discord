import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import atualizar_fichas_supabase 

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="registrar_carteira", description="[MESTRE] Ativa o sistema de moedas na ficha de um sobrevivente")
    @app_commands.describe(alvo="O jogador que terá a carteira inicializada com 0")
    async def registrar_moedas(self, interaction: discord.Interaction, alvo: discord.Member):
        # --- VERIFICAÇÃO DE MESTRE ---
        # Substitua pelo seu ID de usuário para garantir que só VOCÊ use
        SEU_ID = 465303026400231434  # Coloque seu ID aqui, Fenix
        
        if interaction.user.id != SEU_ID:
            return await interaction.response.send_message(
                "❌ Apenas o **Senhor Airton** tem autorização para liberar fundos no Protocolo Fenix.", 
                ephemeral=True
            )

        uid_alvo = str(alvo.id)
        
        # Define 0 moedas como valor inicial permanente no banco
        dados = {"moedas": 0}

        # Tenta atualizar no Supabase
        sucesso = atualizar_fichas_supabase(uid_alvo, dados)

        if sucesso:
            embed = discord.Embed(
                title="💳 Carteira Registrada", 
                description=f"O sistema de capital foi vinculado à identidade de **{alvo.display_name}**.\nSaldo inicial: **0 moedas**.",
                color=0x2ecc71
            )
            embed.set_footer(text="Projeto Fenix | Autorização Administrativa")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"❌ Erro: **{alvo.display_name}** ainda não possui uma ficha base no sistema.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Economia(bot))