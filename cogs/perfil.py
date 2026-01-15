import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas

class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="perfil", aliases=["p", "ficha"])
    async def exibir_perfil(self, ctx, alvo: discord.Member = None):
        alvo = alvo or ctx.author
        uid = str(alvo.id)
        fichas = carregar_fichas()

        if uid not in fichas:
            return await ctx.send(f"❌ {'Você' if alvo == ctx.author else alvo.display_name} ainda não possui um registro no sistema.")

        f = fichas[uid]
        info = f["informacoes"]
        st = f["status"]
        vantagens = f.get("vantagens", [])
        desvantagens = f.get("desvantagens", [])

        embed = discord.Embed(
            title=f"👤 Registro Bio-Sinergia: {info['nome']}",
            description=f"**Setor:** Vitória de Santo Antão | **Ano:** 2030",
            color=0x2b2d31
        )

        if alvo.avatar:
            embed.set_thumbnail(url=alvo.avatar.url)

        # Dados Pessoais
        dados_txt = (
            f"🎂 **Idade:** {info['idade']} anos\n"
            f"💼 **Estágio:** {info['profissao']}\n"
            f"📈 **Pontos Extras:** `{info.get('pontos', 0)}`"
        )
        embed.add_field(name="📋 Biometria", value=dados_txt, inline=False)

        # Atributos (Formatados em grade)
        atributos_txt = (
            f"```arm\n"
            f"FOR: {st['forca']:02d} | VIG: {st['vigor']:02d}\n"
            f"DES: {st['destreza']:02d} | PER: {st['percepcao']:02d}\n"
            f"INT: {st['inteligencia']:02d} | CAR: {st['carisma']:02d}\n"
            f"```"
        )
        embed.add_field(name="⚙️ Atributos", value=atributos_txt, inline=False)

        # Traços de Personalidade (Vantagens e Desvantagens)
        v_lista = ", ".join(vantagens) if vantagens else "Nenhuma"
        d_lista = ", ".join(desvantagens) if desvantagens else "Nenhuma"

        embed.add_field(name="🟢 Vantagens", value=f"*{v_lista}*", inline=True)
        embed.add_field(name="🔴 Desvantagens", value=f"*{d_lista}*", inline=True)

        embed.set_footer(text="Protocolo Fenix | Autorizado pela Bio-Sinergia")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Perfil(bot))