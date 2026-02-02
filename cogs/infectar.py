import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import atualizar_fichas_supabase

class SistemaZumbi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ID real do Senhor Airton (Fenix)
        self.MESTRE_ID = 465303026400231434 

    @app_commands.command(name="infectar", description="[MESTRE] Adiciona ou regrida estágios do Projeto Éden")
    @app_commands.describe(
        acao="Deseja evoluir ou regredir a infecção?",
        alvo="O sobrevivente",
        estagio="O estágio atual que você quer aplicar ou remover"
    )
    @app_commands.choices(
        acao=[
            app_commands.Choice(name="Adicionar (Evoluir)", value="add"),
            app_commands.Choice(name="Remover (Regredir)", value="remove")
        ],
        estagio=[
            app_commands.Choice(name="Estágio 1: Incubação", value=1),
            app_commands.Choice(name="Estágio 2: Febre Ativa", value=2),
            app_commands.Choice(name="Estágio 3: Delírio", value=3),
            app_commands.Choice(name="Estágio 4: Necrose", value=4),
            app_commands.Choice(name="Cura Total (Zerar)", value=0)
        ]
    )
    async def infectar(self, interaction: discord.Interaction, acao: str, alvo: discord.Member, estagio: app_commands.Choice[int]):
        if interaction.user.id != self.MESTRE_ID:
            return await interaction.response.send_message("❌ Apenas o Senhor Airton tem acesso ao Protocolo Éden.", ephemeral=True)

        uid_alvo = str(alvo.id)
        
        # Mapeamento de Status
        mapa = {
            0: {"pct": 0, "nome": "OK", "cor": 0x2ecc71},
            1: {"pct": 25, "nome": "Incubação", "cor": 0x55efc4},
            2: {"pct": 50, "nome": "Febre Ativa", "cor": 0xf1c40f},
            3: {"pct": 75, "nome": "Delírio Cognitivo", "cor": 0xe67e22},
            4: {"pct": 100, "nome": "Necrose Avançada", "cor": 0xc0392b}
        }

        # Caso seja CURA TOTAL
        if estagio.value == 0:
            atualizar_fichas_supabase(uid_alvo, {"infeccao_porcentagem": 0, "estado": "OK"})
            return await interaction.response.send_message(f"💊 **SISTEMA LIMPO:** O sangue de **{alvo.display_name}** está livre do vírus.")

        if acao == "add":
            # Seta exatamente o estágio escolhido
            alvo_info = mapa[estagio.value]
            titulo = "☣️ Evolução Viral"
            desc = f"O vírus avançou no organismo de **{alvo.display_name}**."
        else:
            # Lógica de Regressão: Se tirar o 2, ele volta pro 1. Se tirar o 1, volta pro 0 (OK).
            nivel_regredido = max(0, estagio.value - 1)
            alvo_info = mapa[nivel_regredido]
            titulo = "💊 Regressão Viral"
            desc = f"O tratamento funcionou! A infecção de **{alvo.display_name}** foi contida parcialmente."

        # Salva no banco de dados
        sucesso = atualizar_fichas_supabase(uid_alvo, {
            "infeccao_porcentagem": alvo_info["pct"],
            "estado": alvo_info["nome"]
        })

        if sucesso:
            embed = discord.Embed(title=titulo, description=desc, color=alvo_info["cor"])
            embed.add_field(name="Status Atual", value=f"**{alvo_info['nome']}**")
            embed.set_footer(text="Projeto Fenix | Gestão de Crise 2030")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Erro: Sobrevivente não encontrado no banco.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SistemaZumbi(bot))