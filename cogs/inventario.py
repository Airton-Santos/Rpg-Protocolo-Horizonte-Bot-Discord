import discord
from discord.ext import commands
# Importamos apenas o carregar_fichas
from utils.db_manager import carregar_fichas

class Inventario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mochila", aliases=["inv", "inventario"])
    async def ver_mochila(self, ctx):
        uid = str(ctx.author.id)
        
        # O db_manager agora busca do Supabase
        fichas = carregar_fichas()

        if uid not in fichas:
            return await ctx.send("❌ Você não possui uma ficha registrada no sistema central.")

        ficha = fichas[uid]
        # Pegamos o inventário ou um dicionário vazio se não existir
        inventario = ficha.get("inventario", {})
        nome_rp = ficha['informacoes'].get('nome', 'Desconhecido')

        embed = discord.Embed(
            title=f"🎒 Mochila de {nome_rp}",
            description="Acessando banco de dados de suprimentos... 2030",
            color=0x2ecc71 # Cor Verde para Inventário
        )

        if not inventario:
            embed.description = "⚠️ **Sua mochila está vazia.**\nExplore Vitória de Santo Antão para encontrar suprimentos."
        else:
            # Formata a lista de itens: "• 5x Bandagem"
            # Adicionei uma ordenação simples para ficar mais bonito
            lista_itens = "\n".join([f"🔹 **{qtd}x** {item}" for item, qtd in sorted(inventario.items())])
            
            # Limite de caracteres do Discord para Fields é 1024
            if len(lista_itens) > 1024:
                lista_itens = lista_itens[:1020] + "..."
                
            embed.add_field(name="📦 Itens Carregados", value=lista_itens, inline=False)

        embed.set_footer(text="SISTEMA FENIX | Protocolo de Inventário")
        
        # Se você tiver uma foto de mochila ou ícone do bot, pode colocar aqui:
        # embed.set_thumbnail(url="link_da_imagem")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventario(bot))