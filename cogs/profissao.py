import discord
from discord import app_commands
from discord.ext import commands
import json
from utils.db_manager import carregar_fichas, salvar_fichas

def carregar_dados_profissoes():
    with open("data/profissoes.json", "r", encoding="utf-8") as f:
        return json.load(f)

# --- SELECT MENU ---
class SelectProfissao(discord.ui.Select):
    def __init__(self, usuario_id, profissoes_json, pai_view):
        self.usuario_id = usuario_id
        self.profissoes_json = profissoes_json
        self.pai_view = pai_view

        options = [
            discord.SelectOption(
                label=info['nome'],
                description=f"Ver bônus de {info['nome']}",
                value=chave
            ) for chave, info in profissoes_json.items()
        ]
        super().__init__(placeholder="Escolha sua especialização em 2030...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.usuario_id:
            return await interaction.response.send_message("❌ Esta tela não é sua!", ephemeral=True)

        escolha_chave = self.values[0]
        self.pai_view.escolha_temporaria = escolha_chave
        prof = self.profissoes_json[escolha_chave]

        # Atualiza o Embed com os detalhes da profissão selecionada
        self.pai_view.embed.title = f"📋 Dossiê: {prof['nome']}"
        self.pai_view.embed.description = f"**Sobre:** {prof['descricao']}\n\n*Clique no botão abaixo para confirmar este estágio.*"
        self.pai_view.embed.color = discord.Color.blue()
        
        await interaction.response.edit_message(embed=self.pai_view.embed, view=self.pai_view)

# --- VIEW ---
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
            return await interaction.response.send_message("❌ Ação negada.", ephemeral=True)

        if not self.escolha_temporaria:
            return await interaction.response.send_message("❌ Selecione uma profissão no menu acima!", ephemeral=True)

        fichas = carregar_fichas()
        if self.usuario_id not in fichas:
            return await interaction.response.send_message("❌ Registro biométrico não encontrado.", ephemeral=True)
            
        ficha = fichas[self.usuario_id]
        prof_atual = ficha["informacoes"].get("profissao")

        if prof_atual and prof_atual not in ["None", "Nenhuma"]:
            return await interaction.response.send_message(f"❌ Você já está registrado como **{prof_atual}**.", ephemeral=True)

        dados_prof = self.profissoes_json[self.escolha_temporaria]

        # 1. Aplica o Nome da Profissão
        ficha["informacoes"]["profissao"] = dados_prof["nome"]

        # 2. Injeção de Atributos (Respeitando o CAP de 50)
        for atributo, valor in dados_prof["bonus"].items():
            valor_atual = ficha["status"].get(atributo, 0)
            ficha["status"][atributo] = min(valor_atual + valor, 50)

        # 3. Entrega de Itens Iniciais
        if "inventario" not in ficha: ficha["inventario"] = {}
        for item_nome, qtd in dados_prof["itens_iniciais"].items():
            ficha["inventario"][item_nome] = ficha["inventario"].get(item_nome, 0) + qtd

        try:
            # Sincroniza com o Supabase
            salvar_fichas({self.usuario_id: ficha})

            # Desabilita a view após o sucesso
            for item in self.children:
                item.disabled = True
            
            self.embed.title = "🔒 Registro Biométrico Atualizado!"
            self.embed.description = (
                f"Você agora é oficialmente um **{dados_prof['nome']}**.\n\n"
                "🔹 Atributos calibrados.\n"
                "🔹 Equipamento inicial enviado para sua `/mochila`."
            )
            self.embed.color = discord.Color.green()

            await interaction.response.edit_message(embed=self.embed, view=self)
            self.stop()
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro Crítico de Sincronização: {e}", ephemeral=True)

# --- COG ---
class Profissao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profissao", description="Escolha sua especialização no Protocolo Fenix")
    async def abrir_profissao(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        fichas = carregar_fichas()

        if uid not in fichas:
            return await interaction.response.send_message("❌ Você precisa de um registro. Use `/criar`.", ephemeral=True)

        prof_atual = fichas[uid]["informacoes"].get("profissao")
        if prof_atual and prof_atual not in ["None", "Nenhuma"]:
            return await interaction.response.send_message(f"❌ Seu registro já consta como: **{prof_atual}**.", ephemeral=True)

        try:
            profissoes_json = carregar_dados_profissoes()
            embed = discord.Embed(
                title="💼 Central de Estágios - Vitória 2030",
                description="Selecione sua especialização abaixo para receber bônus e itens.",
                color=0x3498db
            )
            view = ViewProfissao(uid, profissoes_json, embed)
            await interaction.response.send_message(embed=embed, view=view)
        except FileNotFoundError:
            await interaction.response.send_message("❌ Erro: O arquivo de profissões não foi encontrado no servidor.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Profissao(bot))