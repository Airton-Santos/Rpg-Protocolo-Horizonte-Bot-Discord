import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio

class Voz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def join(self, ctx):
        """Faz o bot entrar no canal de voz do usuário"""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
            await ctx.send(f"✅ **Sistemas de voz iniciados no canal:** `{channel.name}`")
        else:
            await ctx.send("❌ Você precisa estar em um canal de voz primeiro!")

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Faz o bot sair do canal de voz"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("🔌 **Sistemas de áudio desconectados.**")
        else:
            await ctx.send("❌ Eu não estou em nenhum canal de voz.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # 1. Ignora mensagens do próprio bot
        if message.author == self.bot.user:
            return

        # 2. Verifica se a mensagem começa com '*' e se o bot está em uma call
        if message.content.startswith('*'):
            texto_para_falar = message.content[1:].strip() # Remove o '*' e espaços
            
            if not texto_para_falar:
                return

            vc = message.guild.voice_client
            if vc and vc.is_connected():
                try:
                    # Gera o arquivo de áudio usando Google TTS
                    tts = gTTS(text=texto_para_falar, lang='pt', tld='com.br')
                    arquivo_audio = f"tts_{message.author.id}.mp3"
                    tts.save(arquivo_audio)

                    # Toca o áudio (usa FFmpeg)
                    if vc.is_playing():
                        vc.stop() # Para o que estiver falando para falar o novo

                    vc.play(discord.FFmpegPCMAudio(source=arquivo_audio), 
                            after=lambda e: os.remove(arquivo_audio)) # Deleta o arquivo após falar
                    
                except Exception as e:
                    print(f"Erro no TTS: {e}")
            else:
                # Opcional: Avisar que ele precisa usar !join antes
                pass

async def setup(bot):
    await bot.add_cog(Voz(bot))