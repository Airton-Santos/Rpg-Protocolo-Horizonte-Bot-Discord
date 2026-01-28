import discord
from discord import app_commands
from discord.ext import commands
from utils.db_manager import salvar_fichas

# --- JANELA POP-UP (MODAL) PARA CRIAR FICHA ---
class ModalCriarFicha(discord.ui.Modal, title="Registro Biométrico - Projeto Fenix"):
    nome = discord.ui.TextInput(
        label="Nome do Personagem",
        placeholder="Ex: Fenix, Jonh Doe...",
        min_length=3,
        max_length=30
    )
    
    idade = discord.ui.TextInput(
        label="Idade do Personagem",
        placeholder="Digite apenas números (Ex: 19)",
        min_length=1,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Validação da idade
        if not self.idade.value.isdigit():
            return await interaction.response.send_message("❌ A idade deve ser um número inteiro!", ephemeral=True)
        
        usuario_id = str(interaction.user.id)
        nome_personagem = self.nome.value.strip()
        idade_personagem = int(self.idade.value)

        # Preparando a estrutura padrão (conforme seu modelo)
        ficha_nova = {
            "informacoes": {
                "nome": nome_personagem,
                "idade": idade_personagem,
                "pontos": 25,
                "pontos_caract": 0,
                "profissao": "Nenhuma",
            },
            "status": {
                "forca": 0, "destreza": 0, "inteligencia": 0,
                "vigor": 0, "percepcao": 0, "carisma": 0
            },
            "vantagens": [],
            "desvantagens": [],
            "inventario": {} 
        }

        try:
            # Salvando no Supabase
            salvar_fichas({usuario_id: ficha_nova})
            
            embed = discord.Embed(
                title="⚔️ Registro Concluído!",
                description=(
                    f"O sistema reconheceu um novo indivíduo.\n\n"
                    f"👤 **Nome:** {nome_personagem}\n"
                    f"🎂 **Idade:** {idade_personagem}\n"
                    f"📈 **Pontos Iniciais:** `25`"
                ),
                color=0x2b2d31
            )
            embed.set_footer(text="Protocolo Fenix | Vitória 2030")
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao salvar no banco: {e}", ephemeral=True)

# --- COG ---
class Ficha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="criar", description="Inicia o registro da sua ficha no sistema")
    async def criar_ficha(self, interaction: discord.Interaction):
        # Abre a janela para o jogador
        await interaction.response.send_modal(ModalCriarFicha())

async def setup(bot):
    await bot.add_cog(Ficha(bot))