import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_fichas

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Exibe os níveis de atributos e pontos disponíveis")
    @app_commands.describe(alvo="Opcional: Ver o status de outro cidadão")
    async def ver_status(self, interaction: discord.Interaction, alvo: discord.Member = None):
        # Define quem será consultado
        usuario = alvo or interaction.user
        uid = str(usuario.id)
        
        # Busca no Supabase
        fichas = carregar_fichas()

        if uid not in fichas:
            msg = "Você não possui um registro no sistema." if alvo is None else f"{usuario.display_name} não possui registro."
            return await interaction.response.send_message(f"❌ {msg}", ephemeral=True)

        f = fichas[uid]
        info = f.get("informacoes", {})
        st = f.get("status", {})

        embed = discord.Embed(
            title=f"📊 Status de Sistema: {info.get('nome', 'Desconhecido')}", 
            color=0x2ecc71,
            description="Acessando biometria via Protocolo..."
        )

        # Informações Básicas (Focado em Progressão)
        dados_bio = (
            f"🎂 **Idade:** {info.get('idade', '??')}\n"
            f"📈 **Pontos Disponíveis:** `{info.get('pontos', 0)}`"
        )
        embed.add_field(name="🧬 Biometria", value=dados_bio, inline=True)
        
        # Profissão / Estágio
        embed.add_field(name="💼 Estágio", value=f"{info.get('profissao', 'Nenhuma')}", inline=True)
        
        # Atributos formatados (Lembrando do CAP de 50)
        status_txt = (
            f"💪 **FOR:** `{st.get('forca', 0):02d}` | 🛡️ **VIG:** `{st.get('vigor', 0):02d}`\n"
            f"🎯 **DES:** `{st.get('destreza', 0):02d}` | 👁️ **PER:** `{st.get('percepcao', 0):02d}`\n"
            f"🧠 **INT:** `{st.get('inteligencia', 0):02d}` | 🗣️ **CAR:** `{st.get('carisma', 0):02d}`"
        )
        embed.add_field(name="⚙️ Atributos (Cap: 50)", value=status_txt, inline=False)
        
        embed.set_footer(text="Sincronizado com Banco de Dados Central | 2030")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))