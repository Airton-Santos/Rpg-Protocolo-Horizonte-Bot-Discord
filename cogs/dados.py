import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os
from utils.db_manager import carregar_fichas

class Dados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Mapeamento para traduzir chaves do JSON para chaves da FICHA
        self.mapa_atributos = {
            "forca": "str",
            "destreza": "dex",
            "inteligencia": "int",
            "percepcao": "per",
            "vigor": "const",
            "carisma": "car"
        }

    def carregar_dados_doencas(self):
        caminho = "data/doencas.json"
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f).get("doencas", [])
        return []

    def realizar_teste(self, uid, atributo_alvo, penalidades_map, bonus_map):
        fichas = carregar_fichas()
        if uid not in fichas:
            return None, "❌ Registro bio-sinergia não encontrado!"

        ficha = fichas[uid]
        status = ficha.get("status", {})
        
        valor_bruto = status.get(atributo_alvo, 0)
        bonus_pelo_status = valor_bruto // 10 
        
        dado = random.randint(1, 20)
        modificador_total = 0
        logs_efeitos = []

        # 1. VERIFICAÇÃO DE DOENÇAS (Desconto direto no teste)
        estado_player = ficha.get("estado", "OK").upper()
        if estado_player != "OK":
            doencas_lista = self.carregar_dados_doencas()
            doenca_ativa = next((d for d in doencas_lista if d["nome"].upper() == estado_player or d["id"].upper() == estado_player), None)
            
            if doenca_ativa:
                penalidades_doenca = doenca_ativa.get("penalidades", {})
                sigla_curta = self.mapa_atributos.get(atributo_alvo)
                
                if sigla_curta in penalidades_doenca:
                    valor_penalidade = penalidades_doenca[sigla_curta]
                    modificador_total += valor_penalidade
                    logs_efeitos.append(f"🦠 **{doenca_ativa['nome']}**: {valor_penalidade}")

        # 2. VERIFICAÇÃO DE TRAITS (Vantagens e Desvantagens)
        player_desv = [d.lower() for d in ficha.get("desvantagens", [])]
        player_vant = [v.lower() for v in ficha.get("vantagens", [])]
        
        for desv_id, (valor, motivo) in penalidades_map.items():
            if desv_id.lower() in player_desv:
                modificador_total -= valor
                logs_efeitos.append(f"📉 {motivo}: -{valor}")

        for vant_id, (valor, motivo) in bonus_map.items():
            if vant_id.lower() in player_vant:
                modificador_total += valor
                logs_efeitos.append(f"📈 {motivo}: +{valor}")

        total_final = dado + bonus_pelo_status + modificador_total
        nome_rp = ficha.get("informacoes", {}).get("nome", "Desconhecido")
        
        return {
            "nome": nome_rp,
            "dado": dado,
            "valor_bruto": valor_bruto,
            "bonus_status": bonus_pelo_status,
            "mod_total": modificador_total,
            "total": total_final,
            "logs": logs_efeitos,
            "doente": estado_player != "OK"
        }, None

    async def enviar_embed(self, interaction: discord.Interaction, titulo, cor, res):
        cor_final = 0xc0392b if res['doente'] else cor
        embed = discord.Embed(title=titulo, color=cor_final)
        embed.set_author(name=f"Personagem: {res['nome']}")
        
        detalhes = f"🎲 Dado: `{res['dado']}`\n"
        detalhes += f"📊 Bônus de Atributo: `+{res['bonus_status']}`\n"
        
        if res['mod_total'] != 0:
            sinal = "+" if res['mod_total'] > 0 else ""
            detalhes += f"⚙️ Modificadores: `{sinal}{res['mod_total']}`"
            
        embed.add_field(name="Decomposição", value=detalhes, inline=True)
        embed.add_field(name="RESULTADO FINAL", value=f"🏆 **{res['total']}**", inline=True)

        if res['logs']:
            embed.add_field(name="Efeitos e Condições", value="\n".join(res['logs']), inline=False)
        
        embed.set_footer(text="Projeto Fenix | Protocolo de Saúde Ativo")
        await interaction.response.send_message(embed=embed)

    # --- COMANDOS COMPLETOS ---

    @app_commands.command(name="tfor", description="Teste de Força")
    async def teste_forca(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        p = {"sedentário": (3, "Sedentário")}
        b = {"lutador amador": (2, "Lutador Amador")}
        res, err = self.realizar_teste(str(user.id), "forca", p, b)
        if err: return await interaction.response.send_message(f"{user.display_name}: {err}", ephemeral=True)
        await self.enviar_embed(interaction, "💪 Teste de Força", 0xe67e22, res)

    @app_commands.command(name="tdex", description="Teste de Destreza")
    async def teste_dex(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        p = {"barulhento": (4, "Barulhento")}
        b = {"atleta": (3, "Atleta")}
        res, err = self.realizar_teste(str(user.id), "destreza", p, b)
        if err: return await interaction.response.send_message(f"{user.display_name}: {err}", ephemeral=True)
        await self.enviar_embed(interaction, "⚡ Teste de Destreza", 0xf1c40f, res)

    @app_commands.command(name="tvig", description="Teste de Vigor")
    async def teste_vigor(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        p = {"asmático": (4, "Asmático")}
        b = {"atleta": (2, "Atleta")}
        res, err = self.realizar_teste(str(user.id), "vigor", p, b)
        if err: return await interaction.response.send_message(f"{user.display_name}: {err}", ephemeral=True)
        await self.enviar_embed(interaction, "🛡️ Teste de Vigor", 0x2ecc71, res)

    @app_commands.command(name="tper", description="Teste de Percepção")
    async def teste_percepcao(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        p = {"miopia": (4, "Miopia")}
        b = {"sentidos aguçados": (3, "Sentidos Aguçados")}
        res, err = self.realizar_teste(str(user.id), "percepcao", p, b)
        if err: return await interaction.response.send_message(f"{user.display_name}: {err}", ephemeral=True)
        await self.enviar_embed(interaction, "👁️ Teste de Percepção", 0x3498db, res)

    @app_commands.command(name="tcar", description="Teste de Carisma")
    async def teste_carisma(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        p = {"pavio curto": (3, "Pavio Curto"), "anti-social": (4, "Anti-Social")}
        b = {"extrovertido": (2, "Extrovertido")}
        res, err = self.realizar_teste(str(user.id), "carisma", p, b)
        if err: return await interaction.response.send_message(f"{user.display_name}: {err}", ephemeral=True)
        await self.enviar_embed(interaction, "🗣️ Teste de Carisma", 0xe91e63, res)

    @app_commands.command(name="tint", description="Teste de Inteligência")
    async def teste_inteligencia(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        p = {"burrice": (5, "Burrice")}
        b = {"inteligência avançada": (3, "Inteligência Avançada")}
        res, err = self.realizar_teste(str(user.id), "inteligencia", p, b)
        if err: return await interaction.response.send_message(f"{user.display_name}: {err}", ephemeral=True)
        await self.enviar_embed(interaction, "🧠 Teste de Inteligência", 0x9b59b6, res)

async def setup(bot):
    await bot.add_cog(Dados(bot))