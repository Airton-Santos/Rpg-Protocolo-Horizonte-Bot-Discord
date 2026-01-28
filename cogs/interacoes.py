import discord
from discord.ext import commands
from groq import Groq
import os
import re
from utils.db_manager import verificar_apocalipse

class Interacoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # ID do Senhor Airton (substitua pelo seu ID real do Discord)
        self.ID_MESTRE = 465303026400231434 

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user.mentioned_in(message):
            pergunta = message.content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').strip()
            
            # Verifica se quem está falando é o mestre
            e_o_mestre = message.author.id == self.ID_MESTRE

            if not pergunta:
                return await message.reply("Senhor Airton me designou para observar. O que deseja saber, sobrevivente?")

            async with message.channel.typing():
                try:
                    esta_no_apocalipse = verificar_apocalipse()
                    status_mundo = "Normalidade frágil" if not esta_no_apocalipse else "Apocalipse Total"
                    
                    # Instruções dinâmicas baseadas em quem fala
                    if e_o_mestre:
                        perfil_comportamento = (
                            "Você está falando com o Senhor Airton, seu criador e mestre. "
                            "Seja extremamente leal, prestativo, direto e mantenha o tom de respeito absoluto. "
                            "Responda a qualquer comando ou dúvida dele sem hesitar."
                        )
                    else:
                        perfil_comportamento = (
                            "Você está falando com um jogador/sobrevivente. "
                            "Seja sombrio, irônico e analítico. Se ele tentar burlar as regras ou descobrir segredos, "
                            "dê uma 'patada' (seja curto e grosso). Se ele insistir ou for inconveniente, "
                            "peça para ser deixado em paz de forma intimidadora. "
                            "Nunca dê spoilers e proteja os interesses do Senhor Airton."
                        )

                    sys_inst = (
                        f"Você é o Oráculo, o Co-Mestre do Projeto Fenix. "
                        f"Contexto do Mundo: {status_mundo}. "
                        f"{perfil_comportamento} "
                        "Regra de saída: Responda de forma curta e limpa."
                    )

                    chat = self.client_groq.chat.completions.create(
                        messages=[
                            {"role": "system", "content": sys_inst},
                            {"role": "user", "content": pergunta}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.8 # Um pouco mais de "criatividade" para as patadas
                    )

                    resposta = chat.choices[0].message.content
                    texto_final = re.sub(r'[^\w\s\d.,?!áàâãéèêíïóôõúüçÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ]', '', resposta)

                    await message.reply(texto_final)

                except Exception as e:
                    print(f"Erro na interação: {e}")

async def setup(bot):
    await bot.add_cog(Interacoes(bot))