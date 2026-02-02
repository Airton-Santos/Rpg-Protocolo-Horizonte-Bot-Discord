import discord
from discord import app_commands
from discord.ext import commands
# Importa as funções do seu gerenciador de banco de dados
from utils.db_manager import carregar_fichas, atualizar_fichas_supabase 

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # COLOQUE SEU ID DE USUÁRIO DO DISCORD AQUI (Ex: 1234567890)
        self.MESTRE_ID = 465303026400231434 

    # --- COMANDO PARA INICIAR A CARTEIRA COM 0 ---
    @app_commands.command(name="registrar_carteira", description="[MESTRE] Ativa o sistema de moedas na ficha de um sobrevivente")
    @app_commands.describe(alvo="O jogador que terá a carteira inicializada com 0")
    async def registrar_moedas(self, interaction: discord.Interaction, alvo: discord.Member):
        if interaction.user.id != self.MESTRE_ID:
            return await interaction.response.send_message("❌ Apenas o Senhor Airton pode autorizar novos registros financeiros.", ephemeral=True)

        uid_alvo = str(alvo.id)
        sucesso = atualizar_fichas_supabase(uid_alvo, {"moedas": 0})

        if sucesso:
            embed = discord.Embed(
                title="💳 Carteira Registrada", 
                description=f"O sistema de capital foi vinculado a **{alvo.display_name}**.\nSaldo inicial: **0 moedas**.",
                color=0x2ecc71
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ Erro: {alvo.display_name} não tem ficha no sistema.", ephemeral=True)

    # --- COMANDO PARA ADICIONAR OU REMOVER MOEDAS ---
    @app_commands.command(name="moedas", description="[MESTRE] Adiciona ou remove moedas de um sobrevivente")
    @app_commands.describe(
        acao="Escolha entre Adicionar ou Remover",
        alvo="O jogador alvo",
        quantidade="Valor a ser alterado"
    )
    @app_commands.choices(acao=[
        app_commands.Choice(name="Adicionar", value="add"),
        app_commands.Choice(name="Remover", value="remove")
    ])
    async def gerenciar_moedas(self, interaction: discord.Interaction, acao: str, alvo: discord.Member, quantidade: int):
        if interaction.user.id != self.MESTRE_ID:
            return await interaction.response.send_message("❌ Acesso negado. Protocolo exclusivo do Senhor Airton.", ephemeral=True)

        if quantidade <= 0:
            return await interaction.response.send_message("❌ A quantidade deve ser maior que zero!", ephemeral=True)

        uid_