import os
from asyncio import sleep
from queue import Queue
from typing import Union, Tuple

import discord
import pytube
from discord.ext import commands
from pytube import YouTube

from config import token, ffmpeg_location

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

song_queue = Queue()
is_playing = False


@client.command(name='play')
async def play(ctx: discord.Message, url: str) -> None:
    """
    Command that triggers the bot to download a YouTube video and play it in the voice channel, which the author of the
    command is connected to.
    :param ctx: Message context
    :param url: URL of the video
    :return: None
    """

    global is_playing

    channel: Union[discord.VoiceClient, None] = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if channel is not None and channel.is_connected() is True:
        vc: discord.VoiceClient = channel
    elif ctx.author.voice is not None:
        vc: discord.VoiceClient = await ctx.author.voice.channel.connect(self_deaf=True)
    else:
        await ctx.channel.send(content="Voice channel not found! :angry:")
        return

    filepath, file_length = download_youtube(url)
    song_queue.put((filepath, file_length))

    if is_playing is False:
        is_playing = True
        while not song_queue.empty():
            song, length = song_queue.get()
            vc.play(
                discord.FFmpegPCMAudio(
                    executable=ffmpeg_location,
                    source=song
                )
            )
            await sleep(length + 3)
            os.remove(song)

        await vc.disconnect()

        is_playing = False


def download_youtube(url: str) -> Tuple[str, int]:
    """
    Downloads the YouTube video as an .mp3 file.
    :param url: URL for the video
    :return: Filepath and length of the downloaded .mp3 file
    """

    yt: YouTube = YouTube(url)
    video: pytube.query.Stream = yt.streams.filter(only_audio=True).first()
    out_file: str = video.download(output_path=os.path.curdir + '\\media')  # Downloads only audio but in .mp4 format

    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'

    if os.path.exists(new_file):
        os.remove(new_file)  # Check if the file already exists. Overwriting is not possible
    os.rename(out_file, new_file)

    return new_file, yt.length


client.run(token)
