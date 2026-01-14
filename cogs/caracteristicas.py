import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas, carregar_caracteristicas

# Tabela de exclusão mútua (Nomes EXATAMENTE como aparecem no JSON)
CONFLITOS = {
    "Atleta": ["Sedentário", "Asmático"],
    "Sedentário": ["Atleta"],
    "Asmático": ["Atleta"],
    "Burrice": ["Inteligência Avançada"],
    "Inteligência Avançada": ["Burrice"],
    "Anti-Social": ["Extrovertido"],
    "Extrovertido": ["Anti-Social"],
    "Hemofílico": ["Cura Rápida"],
    "Cura Rápida": ["Hemofílico"],
    "Miopia": ["Sentidos Aguçados"],
    "Sentidos Aguçados": ["Miopia"]
}

class MenuCaracteristicas(discord.ui.Select):
    def __init__(self, tipo, usuario_id, opcoes_json, pai_view):
        self.tipo = tipo
        self.usuario_id = usuario_id
        self.opcoes_json = opcoes_json
        self.pai_view = pai_view

        options = [
            discord.SelectOption(
                label=f"{info['nome']} ({info['custo']} pts)",
                description=info['desc'][:100],
                value=chave
            ) for chave, info in opcoes_json.items()
        ]
        super().__init__(placeholder=f"Escolha suas {tipo} (Máx 5)...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.usuario_id:
            return await interaction.response.send_message("❌ Esta tela não é sua!", ephemeral=True)

        fichas = carregar_fichas()
        ficha = fichas[self.usuario_id]
        escolha_chave = self.values[0]
        item = self.opcoes_json[escolha_chave]
        nome_escolha = item["nome"]

        # --- VERIFICAÇÃO DE CONFLITOS (EX: SEDENTÁRIO VS ATLETA) ---
        todas_caract = ficha.get("vantagens", []) + ficha.get("desvantagens", [])
        
        if nome_escolha in CONFLITOS:
            for conflito in CONFLITOS[nome_escolha]:
                if conflito in todas_caract:
                    return await interaction.response.send_message(
                        f"❌ Conflito detectado! Você não pode ter **{nome_escolha}** e **{conflito}** ao mesmo tempo.", 
                        ephemeral=True
                    )

        # Garantir campos básicos
        if "pontos_caract" not in ficha["informacoes"]:
            ficha["informacoes"]["pontos_caract"] = 0
        if self.tipo not in ficha:
            ficha[self.tipo] = []

        # Verificação de Limite e Repetição
        if len(ficha[self.tipo]) >= 5:
            return await interaction.response.send_message(f"❌ Limite de 5 {self.tipo} atingido!", ephemeral=True)

        if nome_escolha in ficha[self.tipo]:
            return await interaction.response.send_message(f"❌ Você já possui {nome_escolha}!", ephemeral=True)

        # Processamento de Pontos
        if self.tipo == "vantagens":
            ficha["informacoes"]["pontos_caract"] -= item["custo"]
        else:
            ficha["informacoes"]["pontos_caract"] += item["custo"]

        ficha[self.tipo].append(nome_escolha)
        salvar_fichas(fichas)

        self.pai_view.embed.description = (
            f"👤 **Personagem:** {ficha['informacoes']['nome']}\n"
            f"⚖️ **Saldo de Características:** `{ficha['informacoes']['pontos_caract']}`\n"
            f"📊 **Vantagens:** {len(ficha['vantagens'])}/5 | **Desvantagens:** {len(ficha['desvantagens'])}/5\n\n"
            f"✅ Selecionado: **{nome_escolha}**"
        )
        
        await interaction.response.edit_message(embed=self.pai_view.embed, view=self.pai_view)

class ViewCaracteristicas(discord.ui.View):
    def __init__(self, usuario_id, embed):
        super().__init__(timeout=300)
        self.usuario_id = usuario_id
        self.embed = embed
        
        vantagens = carregar_caracteristicas("vantagens")
        desvantagens = carregar_caracteristicas("desvantagens")
        
        self.add_item(MenuCaracteristicas("vantagens", usuario_id, vantagens, self))
        self.add_item(MenuCaracteristicas("desvantagens", usuario_id, desvantagens, self))

    @discord.ui.button(label="Confirmar Escolhas", style=discord.ButtonStyle.success, emoji="🔒")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.usuario_id:
            return await interaction.response.send_message("❌ Esta tela não é sua!", ephemeral=True)

        for item in self.children:
            item.disabled = True
        
        self.embed.color = discord.Color.greyple()
        self.embed.title = "🔒 Customização Finalizada"
        self.embed.set_footer(text="Escolhas travadas com sucesso.")

        await interaction.response.edit_message(embed=self.embed, view=self)
        self.stop()

class Caracteristicas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="caracteristicas")
    async def abrir_menu(self, ctx):
        uid = str(ctx.author.id)
        fichas = carregar_fichas()
        if uid not in fichas:
            return await ctx.send("❌ Crie sua ficha primeiro!")

        ficha = fichas[uid]
        saldo = ficha["informacoes"].get("pontos_caract", 0)
        
        embed = discord.Embed(
            title="🎭 Sistema de Características",
            description=(f"👤 **Personagem:** {ficha['informacoes']['nome']}\n"
                         f"⚖️ **Saldo de Características:** `{saldo}`\n"
                         f"📊 **Vantagens:** {len(ficha.get('vantagens', []))}/5 | **Desvantagens:** {len(ficha.get('desvantagens', []))}/5"),
            color=0x9b59b6
        )
        
        view = ViewCaracteristicas(uid, embed)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Caracteristicas(bot))