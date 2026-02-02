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
        self.mapa_atributos = {
            "forca": "str",
            "destreza": "dex",
            "inteligencia": "int",
            "percepcao": "per",
            "vigor": "const",
            "carisma": "car"
        }

    def carregar_dados_doencas(self):
        """Lê doenças extras do arquivo JSON local."""
        caminho = "data/doencas.json"
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f).get("doencas", [])
        return []

    def calcular_debuff_eden(self, porcentagem, atributo):
        """Penalidades fixas da Lore do Projeto Éden."""
        if porcentagem <= 0: return 0, None
        
        if 1 <= porcentagem <= 25:
            if atributo == "percepcao": return -1, "🟢 Éden: Incubação"
        elif 26 <= porcentagem <= 50:
            if atributo in ["destreza", "forca"]: return -2, "🟡 Éden: Febre Ativa"
            if atributo == "percepcao": return -1, "🟡 Éden: Febre Ativa"
        elif 51 <= porcentagem <= 75:
            if atributo in ["inteligencia", "carisma"]: return -3, "🟠 Éden: Delírio"
            if atributo in ["destreza", "forca"]: return -2, "🟠 Éden: Delírio"
            if atributo == "percepcao": return -1, "🟠 Éden: Delírio"
        elif porcentagem > 75:
            return -5, "🔴 Éden: Necrose Avançada"
            
        return 0, None

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

        # 1. VERIFICAÇÃO DO PROJETO ÉDEN (Baseado em %)
        porcentagem_infec = ficha.get("infeccao_porcentagem", 0)
        debuff_eden, nome_estagio = self.calcular_debuff_eden(porcentagem_infec, atributo_alvo)
        if debuff_eden != 0:
            modificador_total += debuff_eden
            logs_efeitos.append(f"☣️ **{nome_estagio}**: {debuff_eden}")

        # 2. VERIFICAÇÃO DE DOENÇAS DO JSON (Baseado no campo 'estado')
        estado_player = str(ficha.get("estado", "OK")).upper()
        if estado_player != "OK":
            doencas_lista = self.carregar_dados_doencas()
            doenca_ativa = next((d for d in doencas_lista if d["nome"].upper() in estado_player or d["id"].upper() in estado_player), None)
            
            if doenca_ativa:
                penalidades_doenca = doenca_ativa.get("penalidades", {})
                sigla_curta = self.mapa_atributos.get(atributo_alvo)
                if sigla_curta in penalidades_doenca:
                    valor_penalidade = penalidades_doenca[sigla_curta]
                    modificador_total += valor_penalidade
                    logs_efeitos.append(f"🦠 **{doenca_ativa['nome']}**: {valor_penalidade}")

        # 3. VERIFICAÇÃO DE TRAITS
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
            "nome": nome_rp, "dado": dado, "bonus_status": bonus_pelo_status,
            "mod_total": modificador_total, "total": total_final, "logs": logs_efeitos,
            "infectado": (porcentagem_infec > 0 or estado_player != "OK")
        }, None

    async def enviar_embed(self, interaction: discord.Interaction, titulo, cor, res):
        cor_final = 0xc0392b if res['infectado'] else cor
        embed = discord.Embed(title=titulo, color=cor_final)
        embed.set_author(name=f"Personagem: {res['nome']}")
        
        detalhes = f"🎲 Dado: `{res['dado']}`\n📊 Atributo: `+{res['bonus_status']}`"
        if res['mod_total'] != 0:
            sinal = "+" if res['mod_total'] > 0 else ""
            detalhes += f"\n⚙️ Mods: `{sinal}{res['mod_total']}`"
            
        embed.add_field(name="Decomposição", value=detalhes, inline=True)
        embed.add_field(name="RESULTADO FINAL", value=f"🏆 **{res['total']}**", inline=True)

        if res['logs']:
            embed.add_field(name="Condições e Efeitos", value="\n".join(res['logs']), inline=False)
        
        embed.set_footer(text="Projeto Fenix | Vitória de Santo Antão 2030")
        await interaction.response.send_message(embed=embed)

    # --- COMANDOS ---
    @app_commands.command(name="tfor", description="Teste de Força")
    async def tfor(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        res, err = self.realizar_teste(str(user.id), "forca", {"sedentário": (3, "Sedentário")}, {"lutador amador": (2, "Lutador Amador")})
        if err: return await interaction.response.send_message(err, ephemeral=True)
        await self.enviar_embed(interaction, "💪 Teste de Força", 0xe67e22, res)

    @app_commands.command(name="tdex", description="Teste de Destreza")
    async def tdex(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        res, err = self.realizar_teste(str(user.id), "destreza", {"barulhento": (4, "Barulhento")}, {"atleta": (3, "Atleta")})
        if err: return await interaction.response.send_message(err, ephemeral=True)
        await self.enviar_embed(interaction, "⚡ Teste de Destreza", 0xf1c40f, res)

    @app_commands.command(name="tvig", description="Teste de Vigor")
    async def tvig(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        res, err = self.realizar_teste(str(user.id), "vigor", {"asmático": (4, "Asmático")}, {"atleta": (2, "Atleta")})
        if err: return await interaction.response.send_message(err, ephemeral=True)
        await self.enviar_embed(interaction, "🛡️ Teste de Vigor", 0x2ecc71, res)

    @app_commands.command(name="tper", description="Teste de Percepção")
    async def tper(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        res, err = self.realizar_teste(str(user.id), "percepcao", {"miopia": (4, "Miopia")}, {"sentidos aguçados": (3, "Sentidos Aguçados")})
        if err: return await interaction.response.send_message(err, ephemeral=True)
        await self.enviar_embed(interaction, "👁️ Teste de Percepção", 0x3498db, res)

    @app_commands.command(name="tcar", description="Teste de Carisma")
    async def tcar(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        res, err = self.realizar_teste(str(user.id), "carisma", {"pavio curto": (3, "Pavio Curto")}, {"extrovertido": (2, "Extrovertido")})
        if err: return await interaction.response.send_message(err, ephemeral=True)
        await self.enviar_embed(interaction, "🗣️ Teste de Carisma", 0xe91e63, res)

    @app_commands.command(name="tint", description="Teste de Inteligência")
    async def tint(self, interaction: discord.Interaction, alvo: discord.Member = None):
        user = alvo or interaction.user
        res, err = self.realizar_teste(str(user.id), "inteligencia", {"burrice": (5, "Burrice")}, {"inteligência avançada": (3, "Inteligência Avançada")})
        if err: return await interaction.response.send_message(err, ephemeral=True)
        await self.enviar_embed(interaction, "🧠 Teste de Inteligência", 0x9b59b6, res)

async def setup(bot):
    await bot.add_cog(Dados(bot))