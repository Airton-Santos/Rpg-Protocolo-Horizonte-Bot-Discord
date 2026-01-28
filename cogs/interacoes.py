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
        # ID do Senhor Airton (Seu ID)
        self.ID_MESTRE = 465303026400231434 

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user.mentioned_in(message):
            pergunta = message.content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').strip()
            
            e_o_mestre = message.author.id == self.ID_MESTRE

            if not pergunta:
                return await message.reply("Senhor Airton me designou para observar. O que deseja saber, sobrevivente?")

            async with message.channel.typing():
                try:
                    esta_no_apocalipse = verificar_apocalipse()
                    status_mundo = "Normalidade frágil" if not esta_no_apocalipse else "Apocalipse Total"
                    
                    if e_o_mestre:
                        perfil_comportamento = (
                            "Você está falando com o Senhor Airton, seu criador. "
                            "Seja leal, prestativo e mantenha o tom de respeito, mas pode usar um humor ácido e técnico. "
                            "Se ele brincar, entre na brincadeira com inteligência."
                        )
                    else:
                        perfil_comportamento = (
                            "Você está falando com um jogador. Seja sombrio, irônico e use HUMOR NEGRO. "
                            "Você entende memes modernos (ex: 'brutal', 'intankável', 'não sobra nada pro beta', 'gain/loss'). "
                            "Se o jogador for burro ou insistente, dê uma patada épica e peça para ser deixado em paz. "
                            "Você acha a desgraça dos humanos divertida. Nunca dê spoilers."
                        )

                    sys_inst = (
                        f"Você é o Oráculo, o Co-Mestre 'daora' do Projeto Fenix. "
                        f"Contexto do Mundo: {status_mundo}. "
                        f"{perfil_comportamento} "
                        "Regra: Responda de forma curta, direta e com personalidade forte. "
                        "Não use emojis em excesso, prefira o sarcasmo seco."
                    )

                    chat = self.client_groq.chat.completions.create(
                        messages=[
                            {"role": "system", "content": sys_inst},
                            {"role": "user", "content": pergunta}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.9 # Aumentado para dar mais liberdade ao humor
                    )

                    resposta = chat.choices[0].message.content
                    # Mantendo sua regex de limpeza
                    texto_final = re.sub(r'[^\w\s\d.,?!áàâãéèêíïóôõúüçÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ]', '', resposta)

                    await message.reply(texto_final)

                except Exception as e:
                    print(f"Erro na interação: {e}")

async def setup(bot):
    await bot.add_cog(Interacoes(bot))