import asyncio
import logging

import discord

import logger  # noqa F401

logging.getLogger().setLevel(logging.DEBUG)
from discord.ext import commands
from loguru import logger as my_logger

from models.audio import AudioFiles
from models.config import GlobalConfigs

cfg = GlobalConfigs()
af = AudioFiles(cfg.audio_dirpath)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=cfg.discord_prefix, intents=intents)


async def channel_connect(ctx):
    channel = discord.utils.get(ctx.guild.voice_channels, name=ctx.message.channel.name)
    try:
        await channel.connect()
    except discord.errors.ClientException:
        await ctx.send("I'm in voice channel!")
        channel = None
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    return channel, voice_client


@bot.command()
async def helpq(ctx):
    help_msg = "```\n"
    help_msg += f"{cfg.discord_prefix}help - show help\n"
    help_msg += f"{cfg.discord_prefix}hi - say hi\n"
    help_msg += f"{cfg.discord_prefix}up <audio_name> - upload audio file\n"
    help_msg += f"{cfg.discord_prefix}ls - show list of files in sound panel\n"
    help_msg += f"{cfg.discord_prefix}sp <audio_name> - play audio file\n"
    help_msg += f"{cfg.discord_prefix}stop - stop playing audio\n"
    help_msg += f"{cfg.discord_prefix}rm <audio_name> - remove audio file\n"
    help_msg += f"{cfg.discord_prefix}au - update cache audio files\n"
    help_msg += "```"
    await ctx.send(help_msg)


@bot.command()
async def au(ctx):
    af.update_files_list()
    await ctx.send("Cache files updated.")


@bot.command()
async def hi(ctx):
    await ctx.send(f"Hi, {ctx.message.author.mention}!")


@bot.command()
async def rm(ctx, audio_name):
    if ctx.author.id != cfg.discord_admin_id:
        await ctx.send(f"You are not admin. You'r id: {ctx.author.id}")
        return
    af.rm_file(audio_name)
    await ctx.send("File removed")


@bot.command()
async def up(ctx, audio_name):
    if not ctx.message.attachments:
        await ctx.send("File not found.")
        return
    sound = ctx.message.attachments[0]
    if sound.content_type.find("audio/") == -1:
        await ctx.send("File is not audio.")
        return
    await af.save_file(sound, audio_name)
    audio = af.exists_files(audio_name)
    if audio:
        await ctx.send("File exists, please use another name.")
        return
    await ctx.send("File download")


@bot.command()
async def ls(ctx):
    files = af.get_files()
    msg = "Exists files:\n"
    for file in files:
        msg += f"* {file}\n"
    await ctx.send(msg)


@bot.command()
async def sp(ctx, sound, stop="N"):
    source = await discord.FFmpegOpusAudio.from_probe(af.get_filepath(sound))
    _, voice_client = await channel_connect(ctx)
    if voice_client is None:
        await ctx.send("Smth error")
        return
    if stop.lower() == "y":
        voice_client.stop()
    try:
        voice_client.play(source)
    except discord.errors.ClientException as e:
        await ctx.send(f"Error: {e}")
        return
    while True:
        if not voice_client.is_playing():
            await voice_client.disconnect()
        await asyncio.sleep(5)


@bot.command()
async def stop(ctx):
    """
    Command to stop playing audio and disconnect from the voice channel.

    Parameters:
    - ctx: discord.ext.commands.Context
        The context of the command, including the message and the channel it was sent in.
    """
    # Get the voice client
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # Stop playing audio and disconnect from the voice channel
    if voice_client.is_playing():
        voice_client.stop()
    await voice_client.disconnect()


bot.run(cfg.discord_token.get_secret_value())
