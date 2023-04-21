from youtubesearchpython.__future__ import VideosSearch

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
import validators

intents = discord.Intents.all()
client = commands.Bot(command_prefix='s', intents=intents, case_insensitive=True)

song_queue: Queue[Tuple[str, int, bool]] = Queue()
is_playing = False


@client.event
async def on_ready() -> None:
    """
    Function that prints an invitation URL after the bot is loaded.
    :return: None
    """

    print(discord.utils.oauth_url(client_id=client.application_id))


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState) -> None:
    """
    Function that gets triggered every time someone leaves/enters a channel. It checks whether a user has disconnected
    and the bot is left alone in a channel. If so, it disconnects it automatically.
    :param member: Member who changed their voice state
    :param before: Voice state before the change
    :param after: Voice state after the change
    :return: None
    """

    # member.guild.voice_client returns either the channel the bot is connected in the particular server or None.
    if member.guild.voice_client is not None:
        # Check if the user left the channel that the bot is currently in and whether the bot is alone.
        if before.channel == member.guild.voice_client.channel and len(before.channel.members) == 1:
            global is_playing

            is_playing = False
            song_queue.empty()
            await member.guild.voice_client.disconnect(force=False)


@client.command(name='join')
async def join(ctx: Message) -> None:
    """
    Command that makes the bot join the channel and play an iconic theme song.
    :param ctx: Message context
    :return: None
    """

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
    """
    Commands that make the bot disconnect from the current channel, clearing the song queue in the process.
    :param ctx: Message context
    :return: None
    """

    global is_playing

    if ctx.guild.voice_client is not None:
        is_playing = False
        song_queue.empty()
        await ctx.guild.voice_client.disconnect(force=True)
        return

    async with ctx.channel.typing():
        await ctx.channel.send(content='I\'m not even connected! :triumph:')


@client.command(name='play')
async def play(ctx: Message, *args) -> None:
    """
    Command that triggers the bot to download a YouTube video and play it in the voice channel, which the author of the
    command is connected to.
    :param ctx: Message context
    :param args: captures the URL / name of the video
    :return: None
    """

    global is_playing

    url = ' '.join(args)
    vc: Union[VoiceClient, None] = await connect_channel(ctx=ctx)

    if vc is None:
        async with ctx.channel.typing():
            await ctx.reply(content="Voice channel not found! :angry:")
            return

    # If the url is not directly provided, search for it
    if not validators.url(url):
        videos_search = VideosSearch(url, limit=1)
        # Interestingly .next() returns ALL results
        videos_result = await videos_search.next()
        url = videos_result['result'][0]['link']

    filepath, file_length, title, thumbnail = await download_youtube(url)
    last_slash = thumbnail.rfind('/')
    thumbnail = thumbnail[:last_slash] + '/mqdefault.jpg'

    # Send a cool embedded message with song details and url
    embedded_message = await create_embedded_message(title, url, thumbnail, ctx.author.avatar, ctx.author.name)
    await ctx.channel.send(embed=embedded_message)

    # The last parameter is whether the file should be deleted after it is played.
    song_queue.put((filepath, file_length, True))

    if not is_playing:
        await play_in_channel(vc=vc)


async def create_embedded_message(title, url, thumbnail, author_avatar, author_name) -> discord.Embed:
    embed = discord.Embed(
        title='Now Playing',
        url='{}'.format(url),
        description='{}'.format(title)
    )
    embed.set_thumbnail(url=thumbnail)
    embed.set_author(name=author_name, icon_url=author_avatar)
    return embed


async def download_youtube(url: str) -> Tuple[str, int, str, str]:
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

    return new_file, yt.length, yt.title, yt.thumbnail_url


async def connect_channel(ctx: Message) -> Union[VoiceClient, None]:
    """
    Function that tries to connect to a voice channel. First it checks whether the bot is already connected and if not,
    it tries connecting to the user's voice channel.
    :param ctx: Message context
    :return: Union[VoiceClient, None]
    """

    channel: Union[VoiceClient, None] = ctx.guild.voice_client

    if channel is not None and channel.is_connected() is True:
        return channel
    elif ctx.author.voice is not None:
        return await ctx.author.voice.channel.connect(self_deaf=True)
    return None


async def play_in_channel(vc: VoiceClient) -> None:
    """
    Function that starts taking songs from the queue and plays them in the provided voice channel.
    :param vc: Voice channel where the bot should play
    :return: None
    """

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
