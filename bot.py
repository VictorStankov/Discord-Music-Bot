import os
from asyncio import sleep

import discord
import pytube
from discord.ext import commands
from pytube import YouTube

from config import token

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)


@client.command(name='play')
async def on_ready(ctx: discord.Message, url: str) -> None:
    """
    Command that triggers the bot to download a YouTube video and play it in the voice channel, which the author of the
    command is connected to.
    :param ctx: Message context
    :param url: URL of the video
    :return: None
    """
    if ctx.author.voice is not None:
        filepath = download_youtube(url)

        channel: discord.VoiceChannel = ctx.author.voice.channel
        vc: discord.VoiceClient = await channel.connect()

        vc.play(discord.FFmpegPCMAudio(
            executable=os.path.curdir + "\\ffmpeg\\bin\\ffmpeg.exe", source=filepath))

        while vc.is_playing():
            await sleep(5)

        os.remove(filepath)
        await vc.disconnect()
    else:
        await ctx.channel.send(content="Voice channel not found! :angry:")


def download_youtube(url: str) -> str:
    """
    Downloads the YouTube video as an .mp3 file.
    :param url: URL for the video
    :return: Filepath of the downloaded .mp3 file
    """

    yt: YouTube = YouTube(url)
    video: pytube.query.Stream = yt.streams.filter(only_audio=True).first()
    out_file: str = video.download(output_path=os.path.curdir + '\\media')  # Downloads only audio but in .mp4 format

    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'

    if os.path.exists(new_file):
        os.remove(new_file)  # Check if the file already exists. Overwriting is not possible
    os.rename(out_file, new_file)

    return new_file


client.run(token)
