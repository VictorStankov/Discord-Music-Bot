import os
from asyncio import sleep
from queue import Queue
from typing import Union, Tuple

import discord
import pytube
from discord import Message, VoiceClient, FFmpegPCMAudio, Member, VoiceState
from discord.ext import commands
from pytube import YouTube

from config import token, ffmpeg_location

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

song_queue = Queue()
is_playing = False


@client.event
async def on_ready():
    print(discord.utils.oauth_url(client_id=client.application_id))


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if after.channel is None and member.guild.voice_client is not None:
        if len(before.channel.members) == 1:
            global is_playing

            is_playing = False
            song_queue.empty()
            await member.guild.voice_client.disconnect(force=False)


@client.command(name='join')
async def join(ctx: Message) -> None:
    if ctx.guild.voice_client is not None:
        async with ctx.channel.typing():
            await ctx.reply(content='Already joined! :rage:')
            return

    vc: Union[VoiceClient, None] = await connect_channel(ctx=ctx)

    if vc is None:
        async with ctx.channel.typing():
            await ctx.reply(content="Voice channel not found! :angry:")
            return

    song_queue.put(('./misc/slavi.wav', 39, False))

    if not is_playing:
        await play_in_channel(vc=vc)


@client.command(name="disconnect", aliases=['dc', 'leave'])
async def disconnect(ctx: Message) -> None:
    global is_playing

    if ctx.guild.voice_client is not None:
        is_playing = False
        song_queue.empty()
        await ctx.guild.voice_client.disconnect(force=True)
        return

    async with ctx.channel.typing():
        await ctx.channel.send(content='I\'m not even connected! :triumph:')


@client.command(name='play')
async def play(ctx: Message, url: str) -> None:
    """
    Command that triggers the bot to download a YouTube video and play it in the voice channel, which the author of the
    command is connected to.
    :param ctx: Message context
    :param url: URL of the video
    :return: None
    """

    global is_playing

    vc: Union[VoiceClient, None] = await connect_channel(ctx=ctx)

    filepath, file_length = await download_youtube(url)
    song_queue.put((filepath, file_length, True))

    if not is_playing:
        await play_in_channel(vc=vc)


async def download_youtube(url: str) -> Tuple[str, int]:
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


async def connect_channel(ctx: Message) -> Union[VoiceClient, None]:
    channel: Union[VoiceClient, None] = ctx.guild.voice_client
    if channel is not None and channel.is_connected() is True:
        return channel
    elif ctx.author.voice is not None:
        return await ctx.author.voice.channel.connect(self_deaf=True)
    return None


async def play_in_channel(vc: VoiceClient) -> None:
    global is_playing

    is_playing = True
    while not song_queue.empty():
        song, length, delete = song_queue.get()
        vc.play(
            FFmpegPCMAudio(
                executable=ffmpeg_location,
                source=song
            )
        )
        await sleep(length + 3)

        if delete:
            os.remove(song)

    is_playing = False

client.run(token)
