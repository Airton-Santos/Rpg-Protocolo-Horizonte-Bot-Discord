import discord
from discord.ext import commands
import asyncio
from utils.db_manager import carregar_fichas, salvar_fichas

class Ficha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="criar")
    @commands.guild_only()
    async def criar_ficha(self, ctx):
        usuario_id = str(ctx.author.id)
        
        # O check agora exige que a mensagem comece com '!'
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.startswith('!')

        # --- PERGUNTA O NOME ---
        await ctx.send("📝 **Qual será o seu nome?**\n(Responda usando `!Nome`, ex: `!Matzin é viado`)")
        try:
            msg_nome = await self.bot.wait_for('message', check=check, timeout=300.0)
            # Remove o '!' do início da mensagem para pegar só o nome
            nome_personagem = msg_nome.content[1:].strip() 
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado! Reinicie com `!criar`.")

        # --- PERGUNTA A IDADE ---
        await ctx.send(f"✅ Nome registrado: **{nome_personagem}**!\nAgora, **qual a idade do personagem?**\n(Responda usando `!Idade`, ex: `!19`)")
        try:
            msg_idade = await self.bot.wait_for('message', check=check, timeout=300.0)
            conteudo_idade = msg_idade.content[1:].strip() # Remove o '!'

            if not conteudo_idade.isdigit():
                return await ctx.send("❌ Você precisa digitar `!` seguido de um **número**! Ex: `!19`. Reinicie com `!criar`.")
            
            idade_personagem = int(conteudo_idade)
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado!")

        # --- SALVANDO NO DATABASE ---
        todas_fichas = carregar_fichas()
        
        todas_fichas[usuario_id] = {
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

        salvar_fichas(todas_fichas)

        embed = discord.Embed(
            title="⚔️ Ficha Registrada!",
            description=f"**Personagem:** {nome_personagem}\n**Idade:** {idade_personagem}",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ficha(bot))