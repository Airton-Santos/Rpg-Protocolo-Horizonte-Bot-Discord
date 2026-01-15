import discord
from discord.ext import commands
import random
from utils.db_manager import carregar_fichas

class Dados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def realizar_teste(self, uid, atributo_alvo, penalidades_map, bonus_map):
        fichas = carregar_fichas()
        if uid not in fichas:
            return None, "❌ Registro bio-sinergia não encontrado! Use `!criar`."

        ficha = fichas[uid]
        status = ficha.get("status", {})
        
        # --- LÓGICA DE STATUS -> BÔNUS (+1 a cada 10) ---
        valor_bruto = status.get(atributo_alvo, 0)
        bonus_pelo_status = valor_bruto // 10  # Divisão inteira: 50/10 = 5 | 25/10 = 2
        
        dado = random.randint(1, 20)
        modificador_traits = 0
        logs_efeitos = []

        player_desv = [d.lower() for d in ficha.get("desvantagens", [])]
        player_vant = [v.lower() for v in ficha.get("vantagens", [])]
        
        # 1. Processar Desvantagens (Traits)
        for desv_id, (valor, motivo) in penalidades_map.items():
            if desv_id.lower() in player_desv:
                modificador_traits -= valor
                logs_efeitos.append(f"📉 {motivo}: -{valor}")

        # 2. Processar Vantagens (Traits)
        for vant_id, (valor, motivo) in bonus_map.items():
            if vant_id.lower() in player_vant:
                modificador_traits += valor
                logs_efeitos.append(f"📈 {motivo}: +{valor}")

        # CÁLCULO FINAL: Dado + Bônus do Atributo + Modificadores de Vantagem/Desvantagem
        total_final = dado + bonus_pelo_status + modificador_traits
        
        nome_rp = ficha.get("informacoes", {}).get("nome", "Desconhecido")
        
        return {
            "nome": nome_rp,
            "dado": dado,
            "valor_bruto": valor_bruto,
            "bonus_status": bonus_pelo_status,
            "mod_traits": modificador_traits,
            "total": total_final,
            "logs": logs_efeitos
        }, None

    async def enviar_embed(self, ctx, titulo, cor, res):
        embed = discord.Embed(title=titulo, color=cor)
        embed.set_author(name=f"Personagem: {res['nome']}")
        
        # Texto detalhando a soma para transparência com o jogador
        detalhes = f"🎲 Dado: `{res['dado']}`\n"
        detalhes += f"📊 Bônus de Atributo: `+{res['bonus_status']}` (Status: {res['valor_bruto']})\n"
        
        if res['mod_traits'] != 0:
            sinal = "+" if res['mod_traits'] > 0 else ""
            detalhes += f"⚙️ Mod. Traits: `{sinal}{res['mod_traits']}`"
            
        embed.add_field(name="Decomposição", value=detalhes, inline=True)
        embed.add_field(name="RESULTADO FINAL", value=f"🏆 **{res['total']}**", inline=True)

        if res['logs']:
            embed.add_field(name="Efeitos Ativos", value="\n".join(res['logs']), inline=False)
        
        embed.set_footer(text="Projeto Fenix | Vitória de Santo Antão 2030")
        await ctx.send(embed=embed)

    # --- COMANDOS DE TESTE ---
    @commands.command(name="tfor")
    async def teste_forca(self, ctx):
        p = {"sedentário": (3, "Sedentário")}
        b = {"lutador amador": (2, "Lutador Amador")}
        res, err = self.realizar_teste(str(ctx.author.id), "forca", p, b)
        if err: return await ctx.send(err)
        await self.enviar_embed(ctx, "💪 Teste de Força", 0xe67e22, res)

    @commands.command(name="tdex")
    async def teste_dex(self, ctx):
        p = {"barulhento": (4, "Barulhento")}
        b = {"atleta": (3, "Atleta")}
        res, err = self.realizar_teste(str(ctx.author.id), "destreza", p, b)
        if err: return await ctx.send(err)
        await self.enviar_embed(ctx, "⚡ Teste de Destreza", 0xf1c40f, res)

    @commands.command(name="tvig")
    async def teste_vigor(self, ctx):
        p = {"asmático": (4, "Asmático"), "sedentário": (2, "Sedentário")}
        b = {"atleta": (2, "Atleta")}
        res, err = self.realizar_teste(str(ctx.author.id), "vigor", p, b)
        if err: return await ctx.send(err)
        await self.enviar_embed(ctx, "🛡️ Teste de Vigor", 0x2ecc71, res)

    @commands.command(name="tper")
    async def teste_percepcao(self, ctx):
        p = {"miopia": (4, "Miopia")}
        b = {"sentidos aguçados": (3, "Sentidos Aguçados")}
        res, err = self.realizar_teste(str(ctx.author.id), "percepcao", p, b)
        if err: return await ctx.send(err)
        await self.enviar_embed(ctx, "👁️ Teste de Percepção", 0x3498db, res)

    @commands.command(name="tcar")
    async def teste_carisma(self, ctx):
        p = {"pavio curto": (3, "Pavio Curto"), "anti-social": (4, "Anti-Social")}
        b = {"extrovertido": (2, "Extrovertido")}
        res, err = self.realizar_teste(str(ctx.author.id), "carisma", p, b)
        if err: return await ctx.send(err)
        await self.enviar_embed(ctx, "🗣️ Teste de Carisma", 0xe91e63, res)

    @commands.command(name="tint")
    async def teste_inteligencia(self, ctx):
        p = {"burrice": (5, "Burrice")}
        b = {"inteligência avançada": (3, "Inteligência Avançada")}
        res, err = self.realizar_teste(str(ctx.author.id), "inteligencia", p, b)
        if err: return await ctx.send(err)
        await self.enviar_embed(ctx, "🧠 Teste de Inteligência", 0x9b59b6, res)

async def setup(bot):
    await bot.add_cog(Dados(bot))