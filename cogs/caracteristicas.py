import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas, carregar_caracteristicas

# Tabela de exclusão mútua
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
        if self.usuario_id not in fichas:
            return await interaction.response.send_message("❌ Ficha não encontrada!", ephemeral=True)
            
        ficha = fichas[self.usuario_id]
        escolha_chave = self.values[0]
        item = self.opcoes_json[escolha_chave]
        nome_escolha = item["nome"]
        custo = item["custo"]

        if "vantagens" not in ficha: ficha["vantagens"] = []
        if "desvantagens" not in ficha: ficha["desvantagens"] = []
        if "informacoes" not in ficha: ficha["informacoes"] = {}
        if "pontos_caract" not in ficha["informacoes"]: ficha["informacoes"]["pontos_caract"] = 0

        lista_atual = ficha.get(self.tipo, [])

        if nome_escolha in lista_atual:
            # DESELECIONAR
            ficha[self.tipo].remove(nome_escolha)
            if self.tipo == "vantagens":
                ficha["informacoes"]["pontos_caract"] += custo
            else:
                ficha["informacoes"]["pontos_caract"] -= custo
            status_msg = f"➖ Removido: **{nome_escolha}**"
        else:
            # SELECIONAR
            todas = ficha["vantagens"] + ficha["desvantagens"]
            if nome_escolha in CONFLITOS:
                for conflito in CONFLITOS[nome_escolha]:
                    if conflito in todas:
                        return await interaction.response.send_message(
                            f"❌ Conflito! Você não pode ter **{nome_escolha}** e **{conflito}**.", ephemeral=True
                        )

            if len(lista_atual) >= 5:
                return await interaction.response.send_message(f"❌ Limite de 5 {self.tipo} atingido!", ephemeral=True)

            if self.tipo == "vantagens":
                ficha["informacoes"]["pontos_caract"] -= custo
            else:
                ficha["informacoes"]["pontos_caract"] += custo

            ficha[self.tipo].append(nome_escolha)
            status_msg = f"✅ Injetado: **{nome_escolha}**"

        try:
            salvar_fichas({self.usuario_id: ficha})
            self.pai_view.embed.description = (
                f"👤 **Personagem:** {ficha['informacoes']['nome']}\n"
                f"⚖️ **Saldo Bio-Sinergia:** `{ficha['informacoes']['pontos_caract']}`\n"
                f"📊 **Vantagens:** {len(ficha['vantagens'])}/5 | **Desvantagens:** {len(ficha['desvantagens'])}/5\n\n"
                f"{status_msg}"
            )
            await interaction.response.edit_message(embed=self.pai_view.embed, view=self.pai_view)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao salvar: {e}", ephemeral=True)

class ViewCaracteristicas(discord.ui.View):
    def __init__(self, usuario_id, embed):
        super().__init__(timeout=300)
        self.usuario_id = usuario_id
        self.embed = embed
        
        vantagens = carregar_caracteristicas("vantagens")
        desvantagens = carregar_caracteristicas("desvantagens")
        
        self.add_item(MenuCaracteristicas("vantagens", usuario_id, vantagens, self))
        self.add_item(MenuCaracteristicas("desvantagens", usuario_id, desvantagens, self))

    @discord.ui.button(label="Finalizar Customização", style=discord.ButtonStyle.success, emoji="🔒")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.usuario_id:
            return await interaction.response.send_message("❌ Esta tela não é sua!", ephemeral=True)

        fichas = carregar_fichas()
        ficha = fichas.get(self.usuario_id)
        
        if ficha["informacoes"].get("pontos_caract", 0) < 0:
            return await interaction.response.send_message("❌ Seu saldo está negativo!", ephemeral=True)

        for item in self.children:
            item.disabled = True
        
        self.embed.color = discord.Color.dark_purple()
        self.embed.title = "🔒 Registro Biométrico Travado"
        await interaction.response.edit_message(embed=self.embed, view=self)
        self.stop()

class Caracteristicas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="caracteristicas", description="Abre o menu de Vantagens e Desvantagens")
    async def abrir_menu(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        fichas = carregar_fichas()
        
        if uid not in fichas:
            return await interaction.response.send_message("❌ Crie sua ficha primeiro!", ephemeral=True)

        ficha = fichas[uid]
        saldo = ficha["informacoes"].get("pontos_caract", 0)
        
        embed = discord.Embed(
            title="🎭 Sistema de Características - Vitória 2030",
            description=(f"👤 **Personagem:** {ficha['informacoes']['nome']}\n"
                         f"⚖️ **Saldo de Pontos:** `{saldo}`\n"
                         f"📊 **Vantagens:** {len(ficha.get('vantagens', []))}/5\n"
                         f"📊 **Desvantagens:** {len(ficha.get('desvantagens', []))}/5"),
            color=0x9b59b6
        )
        embed.set_footer(text="Clique em uma opção já selecionada para removê-la.")
        
        view = ViewCaracteristicas(uid, embed)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Caracteristicas(bot))