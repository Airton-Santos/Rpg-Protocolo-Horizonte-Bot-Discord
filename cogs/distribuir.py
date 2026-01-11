import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas

# --- MODAL: A caixinha que aparece para digitar o número ---
class ModalQuantidade(discord.ui.Modal, title="Distribuir Pontos"):
    quantidade = discord.ui.TextInput(
        label="Quanto quer adicionar?",
        placeholder="Digite um número (ex: 5)",
        min_length=1,
        max_length=2
    )

    def __init__(self, atributo, usuario_id):
        super().__init__()
        self.atributo = atributo
        self.usuario_id = usuario_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valor = int(self.quantidade.value)
            fichas = carregar_fichas()
            ficha = fichas[self.usuario_id]
            
            pontos_atuais = ficha["informacoes"]["pontos"]

            if valor <= 0:
                return await interaction.response.send_message("❌ Digite um valor maior que 0!", ephemeral=True)
            
            if pontos_atuais < valor:
                return await interaction.response.send_message(f"❌ Você só tem {pontos_atuais} pontos!", ephemeral=True)

            # Atualiza os dados
            ficha["status"][self.atributo] += valor
            ficha["informacoes"]["pontos"] -= valor
            salvar_fichas(fichas)

            await interaction.response.send_message(
                f"✅ Sucesso! **{self.atributo.upper()}** agora é **{ficha['status'][self.atributo]}**.\nRestam {ficha['informacoes']['pontos']} pontos.",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message("❌ Por favor, digite apenas números!", ephemeral=True)

# --- VIEW: Os botões que aparecem no chat ---
class ViewDistribuir(discord.ui.View):
    def __init__(self, usuario_id, pontos_disponiveis):
        super().__init__(timeout=None)
        self.usuario_id = usuario_id
        self.pontos = pontos_disponiveis

    async def abrir_modal(self, interaction, atributo):
        if str(interaction.user.id) != self.usuario_id:
            return await interaction.response.send_message("❌ Essa tela não é sua!", ephemeral=True)
        
        await interaction.response.send_modal(ModalQuantidade(atributo, self.usuario_id))

    @discord.ui.button(label="FORÇA", style=discord.ButtonStyle.danger, custom_id="for")
    async def forca(self, interaction, button): await self.abrir_modal(interaction, "forca")

    @discord.ui.button(label="DESTREZA", style=discord.ButtonStyle.success, custom_id="des")
    async def destreza(self, interaction, button): await self.abrir_modal(interaction, "destreza")

    @discord.ui.button(label="INTELIGÊNCIA", style=discord.ButtonStyle.primary, custom_id="int")
    async def inteligência(self, interaction, button): await self.abrir_modal(interaction, "inteligencia")

    @discord.ui.button(label="VIGOR", style=discord.ButtonStyle.secondary, custom_id="vig")
    async def vigor(self, interaction, button): await self.abrir_modal(interaction, "vigor")

    @discord.ui.button(label="PERCEPÇÃO", style=discord.ButtonStyle.secondary, custom_id="per")
    async def percepcao(self, interaction, button): await self.abrir_modal(interaction, "percepcao")

    @discord.ui.button(label="CARISMA", style=discord.ButtonStyle.secondary, custom_id="car")
    async def carisma(self, interaction, button): await self.abrir_modal(interaction, "carisma")

# --- COG: O Comando principal ---
class Evolucao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="distribuir")
    async def distribuir(self, ctx):
        fichas = carregar_fichas()
        uid = str(ctx.author.id)

        if uid not in fichas:
            return await ctx.send("❌ Você não tem uma ficha! Use `!criar`.")

        pontos = fichas[uid]["informacoes"]["pontos"]
        
        if pontos <= 0:
            return await ctx.send("❌ Você não tem mais pontos para distribuir!")

        embed = discord.Embed(
            title="🛠️ Painel de Evolução",
            description=f"Você tem **{pontos}** pontos disponíveis.\nClique no botão do atributo que deseja aumentar!",
            color=0xFFAA00
        )
        
        view = ViewDistribuir(uid, pontos)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Evolucao(bot))