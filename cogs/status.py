import discord
from discord.ext import commands
from utils.db_manager import carregar_fichas

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status")
    @commands.guild_only()
    async def ver_status(self, ctx):
        fichas = carregar_fichas()
        uid = str(ctx.author.id)

        if uid not in fichas:
            return await ctx.send("❌ Você não possui registro. Use `!criar`.")

        f = fichas[uid]
        info, st = f["informacoes"], f["status"]

        embed = discord.Embed(title=f"📊 Status: {info['nome']}", color=0x2ecc71)
        embed.add_field(name="🧬 Status", value=f"Idade: {info['idade']}\nPontos: {info['pontos']}\nProfissão: {info['profissao']}", inline=True)
        
        status_txt = f"💪 FOR: {st['forca']} | 🎯 DES: {st['destreza']} | 🧠 INT: {st['inteligencia']}\n🛡️ VIG: {st['vigor']} | 👁️ PER: {st['percepcao']} | 🗣️ CAR: {st['carisma']}"
        embed.add_field(name="⚙️ Atributos", value=status_txt, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))