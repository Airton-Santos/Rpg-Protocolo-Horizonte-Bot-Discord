import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_fichas

class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="perfil", description="Exibe o registro biométrico e atributos de um cidadão")
    @app_commands.describe(alvo="Opcional: Marque um jogador para ver o perfil dele")
    async def exibir_perfil(self, interaction: discord.Interaction, alvo: discord.Member = None):
        alvo = alvo or interaction.user
        uid = str(alvo.id)
        
        # Busca no Supabase através do db_manager
        fichas = carregar_fichas()

        if uid not in fichas:
            msg = "Você ainda não possui um registro no sistema." if alvo == interaction.user else f"{alvo.display_name} ainda não possui um registro no sistema."
            return await interaction.response.send_message(f"❌ {msg} Use `/criar` para começar.", ephemeral=True)

        f = fichas[uid]
        info = f.get("informacoes", {})
        st = f.get("status", {})
        vantagens = f.get("vantagens", [])
        desvantagens = f.get("desvantagens", [])

        embed = discord.Embed(
            title=f"👤 Registro Bio-Sinergia: {info.get('nome', 'Desconhecido')}",
            description=f"**Setor:** Vitória de Santo Antão | **Ano:** 2030",
            color=0x2b2d31
        )

        # Avatar do jogador
        if alvo.display_avatar:
            embed.set_thumbnail(url=alvo.display_avatar.url)

        # Dados Pessoais
        dados_txt = (
            f"🎂 **Idade:** {info.get('idade', '??')} anos\n"
            f"💼 **Estágio:** {info.get('profissao', 'Nenhum')}\n"
            f"📈 **Pontos Extras:** `{info.get('pontos', 0)}`"
        )
        embed.add_field(name="📋 Biometria", value=dados_txt, inline=False)

        # Atributos (Grade formatada para visual de terminal)
        # O :02d garante o alinhamento (01, 10, 25...)
        atributos_txt = (
            f"```arm\n"
            f"FOR: {st.get('forca', 0):02d} | VIG: {st.get('vigor', 0):02d}\n"
            f"DES: {st.get('destreza', 0):02d} | PER: {st.get('percepcao', 0):02d}\n"
            f"INT: {st.get('inteligencia', 0):02d} | CAR: {st.get('carisma', 0):02d}\n"
            f"```"
        )
        embed.add_field(name="⚙️ Atributos", value=atributos_txt, inline=False)

        # Traços de Personalidade
        v_lista = ", ".join(vantagens) if vantagens else "Nenhuma"
        d_lista = ", ".join(desvantagens) if desvantagens else "Nenhuma"

        embed.add_field(name="🟢 Vantagens", value=f"*{v_lista}*", inline=True)
        embed.add_field(name="🔴 Desvantagens", value=f"*{d_lista}*", inline=True)

        embed.set_footer(text="PROTOCOLO FENIX | Vitória 2030")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Perfil(bot))