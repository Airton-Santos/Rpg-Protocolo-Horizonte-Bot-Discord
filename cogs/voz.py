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
            try:
                if ctx.voice_client is not None:
                    await ctx.voice_client.move_to(channel)
                else:
                    await channel.connect()
                await ctx.send(f"✅ **Sistemas de voz iniciados no canal:** `{channel.name}`")
            except Exception as e:
                await ctx.send(f"❌ **Erro ao conectar:** `{e}`")
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

        # 2. Verifica se a mensagem começa com '*'
        if message.content.startswith('*'):
            texto_para_falar = message.content[1:].strip()
            
            if not texto_para_falar:
                return

            vc = message.guild.voice_client
            
            # Se o bot não estiver na call, avisa o player
            if not vc or not vc.is_connected():
                return await message.channel.send("⚠️ O bot não está em um canal de voz! Use `!join` primeiro.")

            try:
                # Gera o arquivo de áudio
                tts = gTTS(text=texto_para_falar, lang='pt', tld='com.br')
                arquivo_audio = f"tts_{message.author.id}.mp3"
                tts.save(arquivo_audio)

                # Pequena espera para garantir que o arquivo foi escrito no disco do Railway
                await asyncio.sleep(0.3)

                if vc.is_playing():
                    vc.stop()

                # CONFIGURAÇÃO PARA LINUX/RAILWAY
                # O ffmpeg precisa de argumentos de reconexão para evitar que o áudio corte
                ffmpeg_options = {
                    'options': '-vn',
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
                }

                def apos_falar(error):
                    if error:
                        print(f"Erro ao finalizar áudio: {error}")
                    if os.path.exists(arquivo_audio):
                        os.remove(arquivo_audio)

                vc.play(discord.FFmpegPCMAudio(source=arquivo_audio, **ffmpeg_options), after=apos_falar)
                
            except Exception as e:
                # LOG DE ERRO DIRETAMENTE NO DISCORD
                await message.channel.send(f"❌ **Erro Crítico no Sistema de Voz:**\n`{str(e)}`")
                print(f"Erro no TTS: {e}")

async def setup(bot):
    await bot.add_cog(Voz(bot))