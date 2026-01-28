import discord
from discord import app_commands
from discord.ext import commands
import json
from utils.db_manager import carregar_fichas

class Conhecimentos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="conhecimentos", description="Escaneia habilidades compatíveis com seus atributos atuais")
    async def verificar_conhecimentos(self, interaction: discord.Interaction):
        # 1. Busca os dados no Supabase usando interaction
        fichas = carregar_fichas()
        uid = str(interaction.user.id)

        if uid not in fichas:
            return await interaction.response.send_message(
                "❌ Você não possui um registro no sistema. Use `/criar`.", 
                ephemeral=True
            )
        
        ficha = fichas[uid]
        status_player = ficha.get("status", {})
        nome_rp = ficha.get("informacoes", {}).get("nome", "Desconhecido")

        # 2. Carrega o arquivo local de requisitos
        try:
            with open("data/requisitos.json", "r", encoding="utf-8") as f:
                requisitos = json.load(f)
        except FileNotFoundError:
            return await interaction.response.send_message(
                "❌ Erro: O arquivo de requisitos do sistema não foi encontrado.", 
                ephemeral=True
            )
            
        embed = discord.Embed(
            title=f"📚 Conhecimentos: {nome_rp}",
            description="Escaneando habilidades compatíveis com sua biometria atual...",
            color=0x00ff00 # Verde Bio-Sinergia
        )

        # 3. Lógica de comparação
        for categoria, itens in requisitos.items():
            liberados = [] 

            for nome_item, exigencias in itens.items():
                pode_usar = True 
                
                # Checa cada requisito (ex: {"inteligencia": 15})
                for atributo, valor_necessario in exigencias.items():
                    if status_player.get(atributo, 0) < valor_necessario:
                        pode_usar = False
                        break 
                
                if pode_usar:
                    liberados.append(f"🔹 {nome_item}")

            # Se houver itens liberados na categoria, adiciona ao Embed
            if liberados:
                nome_categoria = categoria.replace("_", " ").title()
                embed.add_field(
                    name=f"➔ {nome_categoria}", 
                    value="\n".join(liberados), 
                    inline=False
                )

        if not embed.fields:
            embed.description = "⚠️ **Nenhum conhecimento técnico detectado.**\nAumente seus atributos para liberar novas habilidades."

        embed.set_footer(text="Sincronizado com Protocolo Fenix | Vitória 2030")
        
        # Resposta oficial do Slash Command
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Conhecimentos(bot))