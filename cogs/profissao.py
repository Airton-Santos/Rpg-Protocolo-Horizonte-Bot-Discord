import discord
from discord.ext import commands
import json
from utils.db_manager import carregar_fichas, salvar_fichas

def carregar_dados_profissoes():
    # O catálogo de profissões pode continuar sendo um JSON local ou no Supabase,
    # mas o bônus deve ser aplicado na ficha que vai para o banco.
    with open("data/profissoes.json", "r", encoding="utf-8") as f:
        return json.load(f)

class SelectProfissao(discord.ui.Select):
    def __init__(self, usuario_id, profissoes_json, pai_view):
        self.usuario_id = usuario_id
        self.profissoes_json = profissoes_json
        self.pai_view = pai_view

        options = [
            discord.SelectOption(
                label=info['nome'],
                description="Ver detalhes da profissão",
                value=chave
            ) for chave, info in profissoes_json.items()
        ]
        super().__init__(placeholder="Escolha seu estágio em 2030...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.usuario_id:
            return await interaction.response.send_message("❌ Esta tela não é sua!", ephemeral=True)

        escolha_chave = self.values[0]
        self.pai_view.escolha_temporaria = escolha_chave
        prof = self.profissoes_json[escolha_chave]

        self.pai_view.embed.title = f"📋 {prof['nome']}"
        self.pai_view.embed.description = f"**Sobre:** {prof['descricao']}\n\n*Clique no botão abaixo para confirmar.*"
        self.pai_view.embed.color = discord.Color.blue()
        
        await interaction.response.edit_message(embed=self.pai_view.embed, view=self.pai_view)

class ViewProfissao(discord.ui.View):
    def __init__(self, usuario_id, profissoes_json, embed):
        super().__init__(timeout=300)
        self.usuario_id = usuario_id
        self.profissoes_json = profissoes_json
        self.embed = embed
        self.escolha_temporaria = None
        
        self.add_item(SelectProfissao(usuario_id, profissoes_json, self))

    @discord.ui.button(label="Confirmar Profissão", style=discord.ButtonStyle.success, emoji="✅")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.usuario_id:
            return await interaction.response.send_message("❌ Esta tela não é sua!", ephemeral=True)

        if not self.escolha_temporaria:
            return await interaction.response.send_message("❌ Selecione uma profissão no menu!", ephemeral=True)

        # 1. Carrega do Supabase
        fichas = carregar_fichas()
        if self.usuario_id not in fichas:
            return await interaction.response.send_message("❌ Ficha não encontrada!", ephemeral=True)
            
        ficha = fichas[self.usuario_id]

        # 2. Verifica se já tem profissão
        prof_atual = ficha["informacoes"].get("profissao")
        if prof_atual and prof_atual not in ["None", "Nenhuma"]:
            return await interaction.response.send_message("❌ Você já possui uma profissão!", ephemeral=True)

        dados_prof = self.profissoes_json[self.escolha_temporaria]

        # 3. Aplica Bônus (Respeitando o CAP de 50)
        ficha["informacoes"]["profissao"] = dados_prof["nome"]

        for atributo, valor in dados_prof["bonus"].items():
            valor_atual = ficha["status"].get(atributo, 0)
            # Aplica o limite máximo de 50 definido em suas regras
            ficha["status"][atributo] = min(valor_atual + valor, 50)

        # 4. Aplica Itens
        if "inventario" not in ficha: ficha["inventario"] = {}
        for item_nome, qtd in dados_prof["itens_iniciais"].items():
            ficha["inventario"][item_nome] = ficha["inventario"].get(item_nome, 0) + qtd

        # 5. SALVA NO SUPABASE (Ajuste crucial aqui)
        try:
            # Enviamos apenas a ficha atualizada para o upsert
            salvar_fichas({self.usuario_id: ficha})

            for item in self.children:
                item.disabled = True
            
            self.embed.title = "🔒 Registro Biométrico Atualizado!"
            self.embed.description = f"Você agora é um **{dados_prof['nome']}**.\nOs bônus de atributos e equipamentos iniciais foram injetados no seu perfil."
            self.embed.color = discord.Color.green()

            await interaction.response.edit_message(embed=self.embed, view=self)
            self.stop()
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao salvar no Supabase: {e}", ephemeral=True)

class Profissao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profissao")
    async def abrir_profissao(self, ctx):
        uid = str(ctx.author.id)
        fichas = carregar_fichas()

        if uid not in fichas:
            return await ctx.send("❌ Você precisa de um registro bio-sinergia. Use `!criar`.")

        prof_atual = fichas[uid]["informacoes"].get("profissao")
        if prof_atual and prof_atual not in ["None", "Nenhuma"]:
            return await ctx.send(f"❌ Seu registro já consta como: **{prof_atual}**.")

        try:
            profissoes_json = carregar_dados_profissoes()
            embed = discord.Embed(
                title="💼 Central de Estágios - Vitória de Santo Antão",
                description="Selecione sua especialização para o Protocolo Fenix.",
                color=0x3498db
            )
            view = ViewProfissao(uid, profissoes_json, embed)
            await ctx.send(embed=embed, view=view)
        except FileNotFoundError:
            await ctx.send("❌ Erro: O arquivo de profissões não foi encontrado no servidor.")

async def setup(bot):
    await bot.add_cog(Profissao(bot))