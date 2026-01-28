import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import carregar_fichas, salvar_fichas

# --- MODAL ATUALIZADO ---
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
            
            if self.usuario_id not in fichas:
                return await interaction.response.send_message("❌ Ficha não encontrada!", ephemeral=True)
                
            ficha = fichas[self.usuario_id]
            pontos_disponiveis = ficha["informacoes"].get("pontos", 0)
            valor_atual_atributo = ficha["status"].get(self.atributo, 0)

            if valor <= 0:
                return await interaction.response.send_message("❌ Digite um valor maior que 0!", ephemeral=True)
            
            if pontos_disponiveis < valor:
                return await interaction.response.send_message(f"❌ Você só tem {pontos_disponiveis} pontos!", ephemeral=True)

            # VERIFICAÇÃO DO CAP DE 50 PONTOS (Conforme sua regra)
            if valor_atual_atributo + valor > 50:
                restante_para_50 = 50 - valor_atual_atributo
                if restante_para_50 <= 0:
                    return await interaction.response.send_message(f"❌ **{self.atributo.upper()}** já está no máximo (50)!", ephemeral=True)
                else:
                    return await interaction.response.send_message(f"❌ Limite excedido! Você só pode adicionar mais **{restante_para_50}** pontos.", ephemeral=True)

            # Atualiza dados
            ficha["status"][self.atributo] += valor
            ficha["informacoes"]["pontos"] -= valor

            try:
                salvar_fichas({self.usuario_id: ficha})
                await interaction.response.send_message(
                    f"✅ **{self.atributo.upper()}** aumentado para **{ficha['status'][self.atributo]}**!\nRestam {ficha['informacoes']['pontos']} pontos.",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(f"❌ Erro ao sincronizar: {e}", ephemeral=True)

        except ValueError:
            await interaction.response.send_message("❌ Digite apenas números inteiros!", ephemeral=True)

# --- VIEW ---
class ViewDistribuir(discord.ui.View):
    def __init__(self, usuario_id):
        super().__init__(timeout=300)
        self.usuario_id = usuario_id

    async def abrir_modal(self, interaction, atributo):
        if str(interaction.user.id) != self.usuario_id:
            return await interaction.response.send_message("❌ Esse painel pertence a outro usuário!", ephemeral=True)
        await interaction.response.send_modal(ModalQuantidade(atributo, self.usuario_id))

    @discord.ui.button(label="FORÇA", style=discord.ButtonStyle.danger)
    async def forca(self, interaction, button): await self.abrir_modal(interaction, "forca")

    @discord.ui.button(label="DESTREZA", style=discord.ButtonStyle.success)
    async def destreza(self, interaction, button): await self.abrir_modal(interaction, "destreza")

    @discord.ui.button(label="INTELIGÊNCIA", style=discord.ButtonStyle.primary)
    async def inteligencia(self, interaction, button): await self.abrir_modal(interaction, "inteligencia")

    @discord.ui.button(label="VIGOR", style=discord.ButtonStyle.secondary)
    async def vigor(self, interaction, button): await self.abrir_modal(interaction, "vigor")

    @discord.ui.button(label="PERCEPÇÃO", style=discord.ButtonStyle.secondary)
    async def percepcao(self, interaction, button): await self.abrir_modal(interaction, "percepcao")

    @discord.ui.button(label="CARISMA", style=discord.ButtonStyle.secondary)
    async def carisma(self, interaction, button): await self.abrir_modal(interaction, "carisma")

# --- COG ---
class Evolucao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="distribuir", description="Abre o painel para distribuir pontos de atributo")
    async def distribuir(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        fichas = carregar_fichas()

        if uid not in fichas:
            return await interaction.response.send_message("❌ Você não tem uma ficha! Use `/criar`.", ephemeral=True)

        pontos = fichas[uid]["informacoes"].get("pontos", 0)
        
        if pontos <= 0:
            return await interaction.response.send_message("❌ Você não possui pontos disponíveis.", ephemeral=True)

        embed = discord.Embed(
            title="🛠️ Painel de Evolução Bio-Sinergia",
            description=(
                f"👤 **Candidato:** {fichas[uid]['informacoes']['nome']}\n"
                f"📈 **Pontos Disponíveis:** `{pontos}`\n\n"
                "Selecione o atributo para upgrade. O limite neural é **50**."
            ),
            color=0xFFAA00
        )
        embed.set_footer(text="Projeto Fenix | Vitória 2030")
        
        view = ViewDistribuir(uid)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Evolucao(bot))