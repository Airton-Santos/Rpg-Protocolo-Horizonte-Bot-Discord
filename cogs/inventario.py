import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_fichas

class Inventario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mochila", description="Verifica o inventário e suprimentos atuais")
    @app_commands.describe(alvo="Opcional: Marque um jogador para ver a mochila dele")
    async def ver_mochila(self, interaction: discord.Interaction, alvo: discord.Member = None):
        # Define quem é o dono da mochila (o autor ou o alvo marcado)
        usuario = alvo or interaction.user
        uid = str(usuario.id)
        
        # O db_manager busca do Supabase
        fichas = carregar_fichas()

        if uid not in fichas:
            msg = "❌ Você não possui uma ficha registrada." if alvo is None else f"❌ {usuario.display_name} não possui ficha registrada."
            return await interaction.response.send_message(msg, ephemeral=True)

        ficha = fichas[uid]
        inventario = ficha.get("inventario", {})
        nome_rp = ficha['informacoes'].get('nome', 'Desconhecido')

        embed = discord.Embed(
            title=f"🎒 Mochila: {nome_rp}",
            description="Acessando banco de dados de suprimentos... 2030",
            color=0x2ecc71 # Verde Suprimento
        )

        if not inventario:
            # Se for a própria mochila, dá o aviso de exploração
            if alvo is None:
                embed.description = "⚠️ **Sua mochila está vazia.**\nExplore a região para encontrar suprimentos."
            else:
                embed.description = f"⚠️ A mochila de **{usuario.display_name}** está vazia."
        else:
            # Formata a lista de itens ordenando por nome
            # Filtramos itens com quantidade 0 caso existam
            itens_validos = {item: qtd for item, qtd in inventario.items() if qtd > 0}
            
            if not itens_validos:
                embed.description = "⚠️ Nenhum item funcional detectado."
            else:
                lista_itens = "\n".join([f"🔹 **{qtd}x** {item}" for item, qtd in sorted(itens_validos.items())])
                
                # Segurança contra estouro de caracteres do Discord
                if len(lista_itens) > 1024:
                    lista_itens = lista_itens[:1020] + "..."
                    
                embed.add_field(name="📦 Itens Carregados", value=lista_itens, inline=False)

        embed.set_footer(text="SISTEMA FENIX | Protocolo de Inventário")
        
        # Resposta pública se for sucesso, mas o erro de ficha é privado (ephemeral)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventario(bot))