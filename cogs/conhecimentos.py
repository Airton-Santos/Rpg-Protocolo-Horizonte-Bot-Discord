import discord # Para criar as mensagens bonitas (Embeds)
from discord.ext import commands # Para registrar o comando no Bot
import json # Para conseguir ler o seu arquivo requisitos.json
from utils.db_manager import carregar_fichas # Para buscar a ficha do player

class Conhecimentos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="conhecimentos")
    async def verificar_conhecimentos(self, ctx):
        #carregar ficha do player
        fichas = carregar_fichas()
        uid = str(ctx.author.id)

        if uid not in fichas:
            return await ctx.send("❌ Crie sua ficha primeiro!")
        
        ficha = fichas[uid]
        status_player = ficha["status"]

        # Carregar dados de requisitos
        with open("data/requisitos.json", "r", encoding="utf-8") as f:
            requisitos = json.load(f)
            
        embed = discord.Embed(
            title=f"📚 Conhecimentos de {ficha['informacoes']['nome']}",
            description="Aqui estão os conhecimentos que seu personagem possui com base nos atributos:",
            color=0x00ff00 # Cor verde
        )

       # Para cada categoria e os itens dentro dela...
        for categoria, itens in requisitos.items():
            liberados = [] # Lista limpa para cada nova categoria

            # ATENÇÃO: Este 'for' abaixo deve estar alinhado (identado) dentro do de cima!
            for nome_item, exigencias in itens.items():
                
                # Vamos assumir que ele pode usar até provar o contrário
                pode_usar = True 
                
                # Agora checamos cada requisito do item (ex: {"forca": 10})
                for atributo, valor_necessario in exigencias.items():
                    # Se o player tiver menos do que o necessário, ele não pode usar
                    if status_player.get(atributo, 0) < valor_necessario:
                        pode_usar = False
                        break # Não precisa checar o resto deste item
                
                # Se após checar todos os atributos ele ainda puder usar...
                if pode_usar:
                    liberados.append(f"✅ {nome_item}")

            # Agora, se houver itens liberados, adicionamos ao Embed
            if liberados:
                # O title() deixa "armas_fogo" como "Armas Fogo"
                nome_categoria = categoria.replace("_", " ").title()
                embed.add_field(
                    name=f"➔ {nome_categoria}", 
                    value="\n".join(liberados), 
                    inline=False
                )

        # Por fim, enviamos a mensagem
        await ctx.send(embed=embed)

# ESTA PARTE ABAIXO É O QUE FALTA:
async def setup(bot):
    await bot.add_cog(Conhecimentos(bot))