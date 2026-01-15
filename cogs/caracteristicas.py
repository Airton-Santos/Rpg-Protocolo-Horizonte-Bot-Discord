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

        # 1. Carregar do Supabase no momento do clique (Dados mais recentes)
        fichas = carregar_fichas()
        if self.usuario_id not in fichas:
            return await interaction.response.send_message("❌ Ficha não encontrada!", ephemeral=True)
            
        ficha = fichas[self.usuario_id]
        escolha_chave = self.values[0]
        item = self.opcoes_json[escolha_chave]
        nome_escolha = item["nome"]

        # Garantir listas básicas
        if "vantagens" not in ficha: ficha["vantagens"] = []
        if "desvantagens" not in ficha: ficha["desvantagens"] = []
        if "pontos_caract" not in ficha["informacoes"]: ficha["informacoes"]["pontos_caract"] = 0

        # 2. VERIFICAÇÃO DE CONFLITOS
        todas_caract = ficha["vantagens"] + ficha["desvantagens"]
        
        if nome_escolha in CONFLITOS:
            for conflito in CONFLITOS[nome_escolha]:
                if conflito in todas_caract:
                    return await interaction.response.send_message(
                        f"❌ Conflito biológico! Você não pode ter **{nome_escolha}** e **{conflito}**.", 
                        ephemeral=True
                    )

        # 3. Verificação de Limite e Repetição
        if len(ficha.get(self.tipo, [])) >= 5:
            return await interaction.response.send_message(f"❌ Limite neural de 5 {self.tipo} atingido!", ephemeral=True)

        if nome_escolha in ficha.get(self.tipo, []):
            return await interaction.response.send_message(f"❌ Você já possui {nome_escolha} em seu registro!", ephemeral=True)

        # 4. Processamento de Pontos
        custo = item["custo"]
        if self.tipo == "vantagens":
            ficha["informacoes"]["pontos_caract"] -= custo
        else:
            ficha["informacoes"]["pontos_caract"] += custo

        ficha[self.tipo].append(nome_escolha)

        # 5. SALVAR NO SUPABASE (Apenas a ficha do player)
        try:
            salvar_fichas({self.usuario_id: ficha})
            
            self.pai_view.embed.description = (
                f"👤 **Personagem:** {ficha['informacoes']['nome']}\n"
                f"⚖️ **Saldo Bio-Sinergia:** `{ficha['informacoes']['pontos_caract']}`\n"
                f"📊 **Vantagens:** {len(ficha['vantagens'])}/5 | **Desvantagens:** {len(ficha['desvantagens'])}/5\n\n"
                f"✅ Injetado com sucesso: **{nome_escolha}**"
            )
            
            await interaction.response.edit_message(embed=self.pai_view.embed, view=self.pai_view)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao sincronizar com o banco: {e}", ephemeral=True)

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

        for item in self.children:
            item.disabled = True
        
        self.embed.color = discord.Color.dark_purple()
        self.embed.title = "🔒 Registro Biométrico Travado"
        self.embed.set_footer(text="Protocolo Fenix | Customização encerrada.")

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
            return await ctx.send("❌ Crie sua ficha primeiro usando `!criar`!")

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
        embed.set_footer(text="Selecione as características nos menus abaixo.")
        
        view = ViewCaracteristicas(uid, embed)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Caracteristicas(bot))