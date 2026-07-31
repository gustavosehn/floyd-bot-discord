import asyncio
import discord
from discord.ext import commands
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

ytdlp_format_options = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdlp = yt_dlp.YoutubeDL(ytdlp_format_options)


class Track:
    def __init__(self, source_url, title, requester):
        self.source_url = source_url
        self.title = title
        self.requester = requester


class GuildPlayer:
    def __init__(self, guild):
        self.guild = guild
        self.queue = []
        self.volume = 1.0
        self.current = None
        self.voice_client = None

    def is_playing(self):
        return self.voice_client is not None and self.voice_client.is_playing()

    async def play_next(self):
        if not self.queue:
            self.current = None
            return

        track = self.queue.pop(0)
        self.current = track

        source = discord.FFmpegPCMAudio(track.source_url, **ffmpeg_options)
        transformed = discord.PCMVolumeTransformer(source, volume=self.volume)

        def after_playback(error):
            fut = asyncio.run_coroutine_threadsafe(self.play_next(), bot.loop)
            try:
                fut.result()
            except Exception:
                pass

        self.voice_client.play(transformed, after=after_playback)

    def set_volume(self, value):
        self.volume = value
        if self.voice_client is not None and self.voice_client.source is not None:
            self.voice_client.source.volume = value


players = {}


def get_player(guild):
    if guild.id not in players:
        players[guild.id] = GuildPlayer(guild)
    return players[guild.id]


async def resolve_track(query, requester):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdlp.extract_info(query, download=False))

    if "entries" in data:
        data = data["entries"][0]

    return Track(data["url"], data.get("title", "Faixa desconhecida"), requester)


@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")


@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("Você precisa estar em um canal de voz para me chamar.")
        return

    channel = ctx.author.voice.channel
    player = get_player(ctx.guild)

    if player.voice_client is not None and player.voice_client.is_connected():
        await player.voice_client.move_to(channel)
    else:
        player.voice_client = await channel.connect()

    await ctx.send(f"Entrei em **{channel.name}**.")


@bot.command(name="leave")
async def leave(ctx):
    player = get_player(ctx.guild)

    if player.voice_client is None or not player.voice_client.is_connected():
        await ctx.send("Eu não estou em nenhum canal de voz.")
        return

    player.queue.clear()
    player.current = None
    await player.voice_client.disconnect()
    player.voice_client = None
    await ctx.send("Saí do canal de voz.")


@bot.command(name="play")
async def play(ctx, *, argumento: str = None):
    player = get_player(ctx.guild)

    if player.voice_client is None or not player.voice_client.is_connected():
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("Você precisa estar em um canal de voz.")
            return
        player.voice_client = await ctx.author.voice.channel.connect()

    query = argumento

    if ctx.message.attachments:
        anexo = ctx.message.attachments[0]
        track = Track(anexo.url, anexo.filename, ctx.author)
        player.queue.append(track)
        await ctx.send(f"Adicionado à fila: **{track.title}**.")
    elif query:
        await ctx.send("Buscando e adicionando à fila...")
        try:
            track = await resolve_track(query, ctx.author)
        except Exception:
            await ctx.send("Não consegui processar essa url ou pesquisa.")
            return
        player.queue.append(track)
        await ctx.send(f"Adicionado à fila: **{track.title}**.")
    else:
        await ctx.send("Envie uma url, uma pesquisa ou um arquivo de áudio após o comando.")
        return

    if not player.is_playing():
        await player.play_next()


@bot.command(name="stop")
async def stop(ctx):
    player = get_player(ctx.guild)
    player.queue.clear()

    if player.voice_client is not None and player.voice_client.is_playing():
        player.voice_client.stop()

    player.current = None
    await ctx.send("Fila de músicas parada e limpa.")


@bot.command(name="volume")
async def volume(ctx, nivel: int = None):
    if nivel is None or nivel < 1:
        await ctx.send("Use `.volume` seguido de um número a partir de 1.")
        return

    player = get_player(ctx.guild)
    player.set_volume(nivel / 100)
    await ctx.send(f"Volume ajustado para **{nivel}**.")


@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="Comandos disponíveis", color=discord.Color.blurple())
    embed.add_field(name=".join", value="Entra no canal de voz de quem chamou.", inline=False)
    embed.add_field(name=".leave", value="Sai do canal de voz.", inline=False)
    embed.add_field(name=".play <url, pesquisa ou anexo>", value="Adiciona uma música à fila.", inline=False)
    embed.add_field(name=".stop", value="Para e limpa toda a fila de músicas.", inline=False)
    embed.add_field(name=".volume <número>", value="Ajusta o volume, a partir de 1.", inline=False)
    embed.add_field(name=".help", value="Mostra esta lista de comandos.", inline=False)
    await ctx.send(embed=embed)


bot.run("PUT_YOUR_TOKEN_HERE")
