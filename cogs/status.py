import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status")
    @commands.guild_only()
    async def ver_status(self, ctx):
        # Busca todas as fichas (que vêm do Supabase via db_manager)
        fichas = carregar_fichas()
        uid = str(ctx.author.id)

        if uid not in fichas:
            return await ctx.send("❌ Você não possui um registro bio-sinergia. Use `!criar`.")

        f = fichas[uid]
        
        # Usamos .get() para evitar erros caso algum dado esteja faltando no banco
        info = f.get("informacoes", {})
        st = f.get("status", {})

        embed = discord.Embed(
            title=f"📊 Status de Sistema: {info.get('nome', 'Desconhecido')}", 
            color=0x2ecc71,
            description="Acessando biometria via Protocolo...."
        )

        # Informações Básicas
        dados_bio = (
            f"🎂 **Idade:** {info.get('idade', '??')}\n"
            f"📈 **Pontos Disponíveis:** `{info.get('pontos', 0)}`"
        )
        embed.add_field(name="🧬 Biometria", value=dados_bio, inline=True)
        
        # Profissão / Estágio
        embed.add_field(name="💼 Estágio", value=f"{info.get('profissao', 'Nenhuma')}", inline=True)
        
        # Atributos formatados (Lembrando do CAP de 50)
        # O :02d mantém o alinhamento visual (01, 05, 10...)
        status_txt = (
            f"💪 **FOR:** `{st.get('forca', 0):02d}` | 🛡️ **VIG:** `{st.get('vigor', 0):02d}`\n"
            f"🎯 **DES:** `{st.get('destreza', 0):02d}` | 👁️ **PER:** `{st.get('percepcao', 0):02d}`\n"
            f"🧠 **INT:** `{st.get('inteligencia', 0):02d}` | 🗣️ **CAR:** `{st.get('carisma', 0):02d}`"
        )
        embed.add_field(name="⚙️ Atributos (Cap: 50)", value=status_txt, inline=False)
        
        embed.set_footer(text="Sincronizado com Banco de Dados Central | 2030")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))