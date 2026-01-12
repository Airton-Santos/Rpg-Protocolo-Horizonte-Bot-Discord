import discord
from discord.ext import commands
import json
from utils.db_manager import carregar_fichas, salvar_fichas

def carregar_dados_profissoes():
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
                description="Clique para ver a descrição",
                value=chave
            ) for chave, info in profissoes_json.items()
        ]
        super().__init__(placeholder="Escolha seu estágio...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.usuario_id:
            return await interaction.response.send_message("❌ Esta tela não é sua!", ephemeral=True)

        escolha_chave = self.values[0]
        self.pai_view.escolha_temporaria = escolha_chave
        prof = self.profissoes_json[escolha_chave]

        # Mostra apenas a DESCRIÇÃO no embed ao selecionar
        self.pai_view.embed.title = f"📋 {prof['nome']}"
        self.pai_view.embed.description = f"**Sobre:** {prof['descricao']}"
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

        fichas = carregar_fichas()
        ficha = fichas[self.usuario_id]

        if ficha["informacoes"].get("profissao") != "None" and ficha["informacoes"].get("profissao") != "Nenhuma":
            return await interaction.response.send_message("❌ Você já possui uma profissão!", ephemeral=True)

        dados_prof = self.profissoes_json[self.escolha_temporaria]

        # APLICAÇÃO SILENCIOSA (Bônus e Itens)
        ficha["informacoes"]["profissao"] = dados_prof["nome"]

        for atributo, valor in dados_prof["bonus"].items():
            valor_atual = ficha["status"].get(atributo, 0)
            novo_valor = min(valor_atual + valor, 50) # Cap de 50 automático
            ficha["status"][atributo] = novo_valor

        for item_nome, qtd in dados_prof["itens_iniciais"].items():
            ficha["inventario"][item_nome] = ficha["inventario"].get(item_nome, 0) + qtd

        salvar_fichas(fichas)

        # Desabilita tudo após confirmar
        for item in self.children:
            item.disabled = True
        
        self.embed.title = "🔒 Escolha Confirmada!"
        self.embed.description = f"Você agora é um **{dados_prof['nome']}**.\nSeus bônus e itens foram aplicados com sucesso."
        self.embed.color = discord.Color.green()

        await interaction.response.edit_message(embed=self.embed, view=self)
        self.stop()

class Profissao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profissao")
    async def abrir_profissao(self, ctx):
        uid = str(ctx.author.id)
        fichas = carregar_fichas()

        if uid not in fichas:
            return await ctx.send("❌ Crie sua ficha primeiro!")

        if fichas[uid]["informacoes"].get("profissao") != "Nenhuma":
            return await ctx.send(f"❌ Você já tem uma profissão!")

        profissoes_json = carregar_dados_profissoes()
        
        embed = discord.Embed(
            title="💼 Escolha seu Estágio",
            description="Selecione uma opção para ler a descrição. Confirme para ganhar seus itens e buffs.",
            color=0x3498db
        )
        
        view = ViewProfissao(uid, profissoes_json, embed)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Profissao(bot))