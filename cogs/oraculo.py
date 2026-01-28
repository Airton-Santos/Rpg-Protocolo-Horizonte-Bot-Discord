import discord
from discord import app_commands
from discord.ext import commands
from groq import Groq  # Usando a biblioteca que você já utiliza
import os
import re
from utils.db_manager import verificar_apocalipse

class Oraculo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # IMPORTANTE: Coloque aqui o ID do seu canal de mestre
        self.ID_CANAL_MESTRE = 123456789012345678 
        
        # Inicializa o cliente usando a API KEY do Grok que você tem no .env
        self.client_grok = Groq(api_key=os.getenv("GROK_API_KEY"))

    @app_commands.command(name="oraculo", description="[MESTRE] Consulta o sistema Grok para sugestões narrativas")
    @app_commands.describe(pergunta="O que aconteceu ou o que você quer planejar?")
    async def consultar_oraculo(self, interaction: discord.Interaction, pergunta: str):
        # 1. Trava de Segurança: Só Administradores
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Acesso negado ao Protocolo Oráculo.", ephemeral=True)

        # 2. Trava de Canal: Só responde no seu QG
        if interaction.channel_id != self.ID_CANAL_MESTRE:
            return await interaction.response.send_message("🤫 O Oráculo é secreto. Use-o no seu canal de mestre.", ephemeral=True)

        await interaction.response.defer(thinking=True)

        try:
            # 3. Verifica o estado atual do mundo no DB
            esta_no_apocalipse = verificar_apocalipse()
            
            if not esta_no_apocalipse:
                status_mundo = (
                    "O mundo AINDA NÃO entrou em apocalipse. O ano é 2030, em Vitória de Santo Antão. "
                    "O clima é de normalidade, mas com mistérios sutis, teorias da conspiração, "
                    "notícias estranhas sobre uma 'gripe' e tensão política. Não fale abertamente de zumbis "
                    "a menos que o mestre pergunte sobre sinais de infecção. Foque em suspense."
                )
            else:
                status_mundo = (
                    "O APOCALIPSE COMEÇOU. Vitória de Santo Antão está em caos. "
                    "Mecânicas de barulho, escassez de recursos, hordas e infecção extrema estão ativas. "
                    "O tom é de terror de sobrevivência e desespero."
                )

            # 4. Prompt de Sistema no estilo Fenix
            sys_inst = (
                f"Você é o Oráculo, o Co-Mestre de um RPG de apocalipse zumbi chamado Projeto Fenix. "
                f"Local: Vitória de Santo Antão, PE. Ano: 2030. "
                f"ESTADO ATUAL: {status_mundo} "
                "Responda ao mestre de forma criativa, sombria, técnica e direta."
            )

            # 5. Chamada ao Grok
            chat = self.client_grok.chat.completions.create(
                messages=[
                    {"role": "system", "content": sys_inst},
                    {"role": "user", "content": pergunta}
                ],
                model="grok-beta", # Nome do modelo Grok
                temperature=0.6
            )

            resposta_bruta = chat.choices[0].message.content
            
            # Aplicando sua Regex de limpeza para manter o padrão do Senhor Airton
            texto_final = re.sub(r'[^\w\s\d.,?!áàâãéèêíïóôõúüçÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ]', '', resposta_bruta)

            # 6. Formatação da Resposta
            embed = discord.Embed(
                title="💀 Oráculo Grok: Protocolo 2030",
                description=texto_final,
                color=0x2f3136 if not esta_no_apocalipse else 0x992d22
            )
            embed.set_footer(text=f"Mundo: {'🔥 APOCALIPSE' if esta_no_apocalipse else '🌐 NORMALIDADE'}")
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Erro na conexão neural com o Grok: {e}")

async def setup(bot):
    await bot.add_cog(Oraculo(bot))