import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from utils.db_manager import salvar_estado_player, buscar_estado_player 

class Saude(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ID_MESTRE = 465303026400231434

    def carregar_nomes_doencas(self):
        """Lê o JSON e retorna uma lista de nomes das doenças para o autocomplete."""
        caminho = "data/doencas.json"
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # Puxa os nomes das doenças
                return [d["nome"] for d in dados.get("doencas", [])]
        return []

    @app_commands.command(name="estado", description="[ADMIN] Define o estado de saúde de um sobrevivente")
    @app_commands.describe(player="O sobrevivente alvo", status="Escolha 'OK' ou uma doença do catálogo")
    async def definir_estado(self, interaction: discord.Interaction, player: discord.Member, status: str):
        if interaction.user.id != self.ID_MESTRE:
            return await interaction.response.send_message("❌ **ACESSO NEGADO.**", ephemeral=True)

        # 1. Validação: O status digitado existe no JSON ou é OK?
        doencas_validas = self.carregar_nomes_doencas()
        status_input = status.strip()
        
        # Se não for OK e não estiver na lista do JSON, o Feni avisa
        if status_input.upper() != "OK" and status_input not in doencas_validas:
            return await interaction.response.send_message(
                f"⚠️ **Erro:** A condição `{status_input}` não consta nos arquivos do Oráculo.\n"
                f"Opções válidas: `OK`, {', '.join(doencas_validas)}", 
                ephemeral=True
            )

        status_final = status_input.upper() if status_input.upper() == "OK" else status_input

        try:
            salvar_estado_player(player.id, status_final)

            if status_final == "OK":
                cor, feni_msg = 0x2ecc71, "Sistemas limpos. Saudável (por enquanto)."
                desc = f"O sobrevivente {player.mention} foi estabilizado."
            else:
                cor, feni_msg = 0xe74c3c, f"Patógeno `{status_final}` confirmado. Loss iminente."
                desc = f"O sobrevivente {player.mention} foi diagnosticado com: **{status_final}**."

            embed = discord.Embed(title="🩺 Bio-Sinergia: Atualização", description=desc, color=cor)
            embed.set_footer(text=f"Feni v2.0 | {feni_msg}")
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Erro: {e}", ephemeral=True)

    # Função de Autocomplete para facilitar sua vida ao digitar
    @definir_estado.autocomplete('status')
    async def estado_autocomplete(self, interaction: discord.Interaction, current: str):
        opcoes = ["OK"] + self.carregar_nomes_doencas()
        return [
            app_commands.Choice(name=opt, value=opt)
            for opt in opcoes if current.lower() in opt.lower()
        ][:25] # Limite do Discord

async def setup(bot):
    await bot.add_cog(Saude(bot))