import asyncio
import logging
import random
import os
from typing import Any, Coroutine

import discord

import logger  # noqa F401

logging.getLogger().setLevel(logging.DEBUG)
from discord.ext import commands
from loguru import logger as my_logger

from models.audio import AudioFiles
from models.config import GlobalConfigs

cfg = GlobalConfigs()
af = AudioFiles(cfg.audio_dirpath)

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix=cfg.discord_prefix, intents=intents)

    async def setup_hook(self) -> Coroutine[Any, Any, None]:
        await self.tree.sync()
        #return super()._async_setup_hook()

bot = Bot()

async def channel_connect(ctx, is_troyan: str, channel_name: str, channel_id: int = 0):
    if is_troyan == "y":
        if channel_name == "":
            channel = discord.utils.get(ctx.guild.voice_channels, name=ctx.message.channel.name)
        if channel_id != 0:
            channel = discord.utils.get(ctx.guild.voice_channels, id=channel_id)
        else:
            channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
    else:
        channel = ctx.message.author.voice.channel
    try:
        await channel.connect()
    except discord.errors.ClientException:
        channel = None
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    return channel, voice_client


@bot.hybrid_command(description="Additional help message")
async def helpq(ctx):
    """
    Additional help message
    """
    help_msg = "```\n"
    help_msg += f"{cfg.discord_prefix}help - show help\n"
    help_msg += f"{cfg.discord_prefix}hi - say hi\n"
    help_msg += f"{cfg.discord_prefix}up <audio_name> - upload audio file\n"
    help_msg += f"{cfg.discord_prefix}ls - show list of files in sound panel\n"
    help_msg += f"{cfg.discord_prefix}p <audio_name> - play audio file\n"
    help_msg += f"{cfg.discord_prefix}stop - stop playing audio\n"
    help_msg += f"{cfg.discord_prefix}rm <audio_name> - remove audio file\n"
    help_msg += f"{cfg.discord_prefix}au - update cache audio files\n"
    help_msg += "```"
    await ctx.send(help_msg)


@bot.hybrid_command(description="Update audio cache")
async def au(ctx):
    """
    Update cache audio files
    """
    af.update_files_list()
    await ctx.send("Cache files updated.")


@bot.hybrid_command(description="Say hi")
async def hi(ctx):
    """
    Say hi
    """
    await ctx.send(f"Hi, {ctx.message.author.mention}!")


@bot.hybrid_command(description="Remove audio.")
async def rm(ctx, audio_name):
    """
    Remove audio
    """
    if ctx.author.id != cfg.discord_admin_id:
        await ctx.send(f"You are not admin. You'r id: {ctx.author.id}")
        return
    af.rm_file(audio_name)
    await ctx.send("File removed")


@bot.command()
async def up(ctx, audio_name):
    """
    Upload audio file
    """
    if not ctx.message.attachments:
        await ctx.send("File not found.")
        return
    sound = ctx.message.attachments[0]
    if sound.content_type.find("audio/") == -1:
        await ctx.send("File is not audio.")
        return
    audio = af.exists_files(audio_name)
    if audio:
        await ctx.send("File exists, please use another name.")
        return
    await af.save_file(sound, audio_name)
    await ctx.send("File download")


@bot.command()
async def channellq(ctx):
    voice_channel_list = ctx.guild.voice_channels
    msg = "Voice channel:\n"    
    for channel in voice_channel_list:
        members = ""
        for member in channel.members:
            members += member.nick + ", "
        msg += f"* name: {channel.name} id: {channel.id} members: {members}\n"
    await ctx.send(msg)


@bot.hybrid_command(description="Get list aviable sound.")
async def ls(ctx):
    """
    Get list aviable sound
    """
    files = af.get_files()
    msg = "Play sound:\n"
    for file in files:
        msg += f"* `{cfg.discord_prefix}p {file}`\n"
    await ctx.send(msg)


@bot.hybrid_command(description="Play audio in another voice channel")
async def troyan(ctx, sound, stop="n", bye="y", channel_name="", channel_id="0"):
    """
    Play sound
    """
    if not channel_id.isdigit():
        await ctx.send("Channel id is not digit.")
    channel_id = int(channel_id)
    if not af.exists_files(sound):
        await ctx.send("Audio not found.")
        return
    source = await discord.FFmpegOpusAudio.from_probe(af.get_filepath(sound))
    _, voice_client = await channel_connect(ctx, "y", channel_name, channel_id)
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
    while bye.lower() == "y" and cfg.bye_audio[0] != "":
      if not voice_client.is_playing():
          source = await discord.FFmpegOpusAudio.from_probe(af.get_filepath(random.choice(cfg.bye_audio)))
          voice_client.play(source)
          break
      await asyncio.sleep(1)
    while True:
        if not voice_client.is_playing():
            await voice_client.disconnect()
        await asyncio.sleep(1)


@bot.hybrid_command(description="Play audio")
async def p(ctx, sound, stop="n", bye="n"):
    """
    Play sound
    """
    if not af.exists_files(sound):
        await ctx.send("Audio not found.")
        return
    source = await discord.FFmpegOpusAudio.from_probe(af.get_filepath(sound))
    _, voice_client = await channel_connect(ctx, "n", "", "")
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
    try:
        await ctx.message.delete()
    except Exception as ex:
        my_logger.error(f"Smth error: {ex}")
    while bye.lower() == "y" and cfg.bye_audio[0] != "":
      if not voice_client.is_playing():
          source = await discord.FFmpegOpusAudio.from_probe(af.get_filepath(random.choice(cfg.bye_audio)))
          voice_client.play(source)
          break
      await asyncio.sleep(1)
    while True:
        if not voice_client.is_playing():
            await voice_client.disconnect()
        await asyncio.sleep(1)


@bot.hybrid_command(description="Tag user kaqfan.")
async def kaqfan(ctx,):
    """
    Tag user kaqfan
    """
    await ctx.message.delete()
    message_list = []
    for channel in ctx.guild.voice_channels:
        channelq = bot.get_channel(channel.id)
        try:
            msg = await channelq.send("<@396178346054123523>")
            message_list.append(msg)
        except:
            my_logger.warning(f"Error send text to channel: {channelq}")
    await asyncio.sleep(2)
    for msg in message_list:
        try:
            await msg.delete()
            my_logger.debug("Delete msg")
        except:
            my_logger.error(f"Failed delete msg: {msg}")


@bot.event
async def on_message(message):
    if message.reference and isinstance(message.reference.resolved, discord.Message):
        replied_to = message.reference.resolved
        if replied_to.type == discord.MessageType.new_member:
            if message.stickers:
                try:
                    await message.delete()
                except:
                    pass
                message_list = []
                for channel in message.guild.voice_channels:
                    channelq = bot.get_channel(channel.id)
                    try:
                        msg = await channelq.send(f"<@{message.author.id}>")
                        message_list.append(msg)
                    except:
                        my_logger.warning(f"Error send text to channel: {channelq}")
                await asyncio.sleep(2)
                for msg in message_list:
                    try:
                        await msg.delete()
                        my_logger.debug("Delete msg")
                    except:
                        my_logger.error(f"Failed delete msg: {msg}")
    await bot.process_commands(message)


@bot.hybrid_group(description="Stop play audio")
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

# bot.setup_hook()
bot.run(cfg.discord_token.get_secret_value())
