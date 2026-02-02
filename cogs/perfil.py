import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_fichas

class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def criar_barra_infeccao(self, pct):
        """Gera uma barra visual de progresso para a infecção."""
        total_blocos = 10
        preenchidos = int(pct / 10)
        vazios = total_blocos - preenchidos
        barra = "█" * preenchidos + "░" * vazios
        return barra

    @app_commands.command(name="perfil", description="Exibe o registro biométrico e atributos de um cidadão")
    @app_commands.describe(alvo="Opcional: Marque um jogador para ver o perfil dele")
    async def exibir_perfil(self, interaction: discord.Interaction, alvo: discord.Member = None):
        alvo = alvo or interaction.user
        uid = str(alvo.id)
        
        fichas = carregar_fichas()

        if uid not in fichas:
            msg = "Você ainda não possui um registro no sistema." if alvo == interaction.user else f"{alvo.display_name} ainda não possui um registro no sistema."
            return await interaction.response.send_message(f"❌ {msg} Use `/criar` para começar.", ephemeral=True)

        f = fichas[uid]
        info = f.get("informacoes", {})
        st = f.get("status", {})
        vantagens = f.get("vantagens", [])
        desvantagens = f.get("desvantagens", [])
        moedas = f.get("moedas", 0)
        
        # --- LÓGICA DE INFECÇÃO ---
        estado_atual = f.get("estado", "Saudável (OK)")
        pct_infec = f.get("infeccao_porcentagem", 0)
        
        embed = discord.Embed(
            title=f"👤 Registro Bio-Sinergia: {info.get('nome', 'Desconhecido')}",
            description=f"**Setor:** Vitória de Santo Antão | **Ano:** 2030",
            color=0x2b2d31
        )

        # --- IMAGEM ---
        foto_rp = f.get("aparencia")
        if foto_rp:
            embed.set_image(url=foto_rp)
            if alvo.display_avatar:
                embed.set_thumbnail(url=alvo.display_avatar.url)
        elif alvo.display_avatar:
            embed.set_image(url=alvo.display_avatar.url)

        # Dados Pessoais
        dados_txt = (
            f"🎂 **Idade:** {info.get('idade', '??')} anos\n"
            f"💼 **Estágio:** {info.get('profissao', 'Nenhum')}\n"
            f"📈 **Pontos Extras:** `{info.get('pontos', 0)}`\n"
            f"💰 **Capital:** `{moedas}` moedas"
        )
        embed.add_field(name="📋 Biometria", value=dados_txt, inline=False)

        # --- CAMPO DE INFECÇÃO (BARRA VISUAL) ---
        if pct_infec > 0:
            barra = self.criar_barra_infeccao(pct_infec)
            # Define o emoji baseado no perigo
            emoji_perigo = "☣️" if pct_infec < 100 else "💀"
            txt_infeccao = f"**Status:** `{estado_atual}`\n`[{barra}]` **{pct_infec}%**"
            embed.add_field(name=f"{emoji_perigo} Alerta de Patógeno: Projeto Éden", value=txt_infeccao, inline=False)
            embed.color = 0xc0392b # Vermelho se estiver infectado
        else:
            embed.add_field(name="🟢 Condição Biológica", value=f"**{estado_atual}**", inline=False)

        # Atributos
        atributos_txt = (
            f"```arm\n"
            f"FOR: {st.get('forca', 0):02d} | VIG: {st.get('vigor', 0):02d}\n"
            f"DES: {st.get('destreza', 0):02d} | PER: {st.get('percepcao', 0):02d}\n"
            f"INT: {st.get('inteligencia', 0):02d} | CAR: {st.get('carisma', 0):02d}\n"
            f"```"
        )
        embed.add_field(name="⚙️ Atributos", value=atributos_txt, inline=False)

        # Traços
        v_lista = ", ".join(vantagens) if vantagens else "Nenhuma"
        d_lista = ", ".join(desvantagens) if desvantagens else "Nenhuma"
        embed.add_field(name="🟢 Vantagens", value=f"*{v_lista}*", inline=True)
        embed.add_field(name="🔴 Desvantagens", value=f"*{d_lista}*", inline=True)

        embed.set_footer(text="PROTOCOLO FENIX | Monitoramento em Tempo Real")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Perfil(bot))