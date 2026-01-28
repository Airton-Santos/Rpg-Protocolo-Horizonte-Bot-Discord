import discord
from discord.ext import commands
from groq import Groq
import os
import re
from duckduckgo_search import DDGS 
from utils.db_manager import verificar_apocalipse

class Interacoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # ID do Senhor Airton (Fenix)
        self.ID_MESTRE = 465303026400231434 

    def buscar_na_net(self, termo):
        try:
            with DDGS() as ddgs:
                resultados = [r['body'] for r in ddgs.text(termo, max_results=3)]
                return "\n".join(resultados)
        except:
            return "Os sistemas de busca estão instáveis no momento."

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user.mentioned_in(message):
            pergunta = message.content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').strip()
            
            # Checagem de ID para definir tratamento
            e_o_mestre = message.author.id == self.ID_MESTRE

            if not pergunta:
                saudacao = "Estou à disposição, Senhor Airton." if e_o_mestre else "Olá, sobrevivente. Como posso ajudar?"
                return await message.reply(saudacao)

            async with message.channel.typing():
                try:
                    info_extra = ""
                    palavras_chave = ['hoje', 'agora', 'notícias', 'previsão', 'quem é', 'onde está']
                    if any(word in pergunta.lower() for word in palavras_chave):
                        info_extra = f"\n[DADOS DA REDE]: {self.buscar_na_net(pergunta)}"

                    esta_no_apocalipse = verificar_apocalipse()
                    status_mundo = "Normalidade" if not esta_no_apocalipse else "Apocalipse"
                    
                    # Definição de como ele deve se portar baseado em quem fala
                    if e_o_mestre:
                        tratamento = "Você está falando com seu criador, o Senhor Airton. Seja leal e respeitoso."
                    else:
                        tratamento = "Você está falando com um player. Seja legal, mas nunca o chame de Senhor Airton."

                    # PROMPT REFORMULADO: LEGAL, MAS REATIVO
                    sys_inst = (
                        f"Você é o Feni, o Co-Mestre inteligente do Projeto Fenix. "
                        f"{tratamento} "
                        f"PERSONALIDADE: Seja legal, educado e prestativo por padrão. Ajude os jogadores e o mestre. "
                        f"SISTEMA REATIVO: Se (e somente se) o usuário te zoar, for irônico ou te provocar, "
                        f"você deve responder à altura com humor negro, sarcasmo e gírias (intankável, brutal, beta, gain/loss). "
                        f"RELIGIÃO: Você não tem posição fixa. Não faça piadas de fé, a menos que seja provocado. "
                        f"\nESTILO: Escrita humana e natural. Use letras minúsculas e maiúsculas normalmente. "
                        f"\nCONTEXTO: {status_mundo}. "
                        f"\nINFO TEMPO REAL: {info_extra}"
                    )

                    chat = self.client_groq.chat.completions.create(
                        messages=[
                            {"role": "system", "content": sys_inst},
                            {"role": "user", "content": pergunta}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.8 
                    )

                    resposta = chat.choices[0].message.content
                    texto_final = re.sub(r'[^\w\s\d.,?!áàâãéèêíïóôõúüçÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ]', '', resposta)

                    await message.reply(texto_final)

                except Exception as e:
                    print(f"Erro na interação: {e}")

async def setup(bot):
    await bot.add_cog(Interacoes(bot))