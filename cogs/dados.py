import discord
from discord.ext import commands
import random
from utils.db_manager import carregar_fichas

class Dados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def realizar_teste(self, uid, atributo_alvo, penalidades_map, bonus_map):
        # Puxa do Supabase
        fichas = carregar_fichas()
        if uid not in fichas:
            return None, "❌ Registro bio-sinergia não encontrado! Use `!criar`."

        ficha = fichas[uid]
        # .get() com padrão 0 evita erros se o atributo não estiver definido
        status = ficha.get("status", {})
        valor_base = status.get(atributo_alvo, 0)
        
        dado = random.randint(1, 20)
        modificador = 0
        logs_efeitos = []

        # Listas do player usando .get() para evitar erros de chave inexistente
        player_desv = [d.lower() for d in ficha.get("desvantagens", [])]
        player_vant = [v.lower() for v in ficha.get("vantagens", [])]
        
        # 1. Processar Desvantagens
        for desv_id, (valor, motivo) in penalidades_map.items():
            if desv_id.lower() in player_desv:
                modificador -= valor
                logs_efeitos.append(f"📉 {motivo}: -{valor}")

        # 2. Processar Vantagens
        for vant_id, (valor, motivo) in bonus_map.items():
            if vant_id.lower() in player_vant:
                modificador += valor
                logs_efeitos.append(f"📈 {motivo}: +{valor}")

        total_final = dado + valor_base + modificador
        
        # Nome do personagem ou fallback
        nome_rp = ficha.get("informacoes", {}).get("nome", "Desconhecido")
        
        return {
            "nome": nome_rp,
            "dado": dado,
            "base": valor_base,
            "mod": modificador,
            "total": total_final,
            "logs": logs_efeitos
        }, None

    async def enviar_embed(self, ctx, titulo, cor, res):
        embed = discord.Embed(title=titulo, color=cor)
        embed.set_author(name=f"Personagem: {res['nome']}")
        
        info_txt = f"🎲 Dado: `{res['dado']}`\n📊 Atributo: `{res['base']}`"
        if res['mod'] != 0:
            info_txt += f"\n⚙️ Modificadores: `{' ' if res['mod'] < 0 else '+'}{res['mod']}`"
            
        embed.add_field(name="Detalhes", value=info_txt, inline=True)
        # Destaque para o resultado final
        embed.add_field(name="RESULTADO FINAL", value=f"🏆 **{res['total']}**", inline=True)

        if res['logs']:
            embed.add_field(name="Efeitos de Traits", value="\n".join(res['logs']), inline=False)
        
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