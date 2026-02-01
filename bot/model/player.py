import asyncio
from typing import List, Union

from discord import FFmpegPCMAudio, VoiceClient, Embed, Guild

from bot import ffmpeg_location
from bot.model import OnlinePlayItem, BasePlayItem


class Player:
    """
    Class for playing music in channels.
    """
    def __init__(self, guild: Guild, play_item: BasePlayItem):
        # `expired` is used for showing when the Player queue is empty and the object has expired. After that a new
        # Player object has to be created in its place.
        self.expired: bool = False
        self.guild: Guild = guild
        self.queue: List[BasePlayItem] = [play_item]
        self.task: asyncio.Task = asyncio.create_task(self.play_in_channel())  # Start background process.

    async def play_in_channel(self) -> None:
        """
        Method for playing songs from the queue. After ffmpeg starts playing, the method is put to sleep for the length
        of the music clip. If there are more songs in the queue remaining, it keeps going. Otherwise, it sets the
        `expired` attribute to True and ends.

        :return: None
        """
        while len(self.queue):
            play_item = self.queue.pop(0)  # Retrieve next play_item.
            before_options = ''

            if not self.guild.voice_client:  # Stop execution if bot has been disconnected.
                self.queue.clear()
                self.expired = True
                return

            vc: Union[VoiceClient, None] = self.guild.voice_client

            # Don't send an embed if the song is internal. Mainly for `join` command.
            if isinstance(play_item, OnlinePlayItem):
                await Player._send_embed(play_item=play_item)
                before_options = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'

            vc.play(
                FFmpegPCMAudio(
                    source=play_item.path,
                    executable=ffmpeg_location,
                    before_options=before_options,  # Reconnect if connection is lost to URL source. Happens often.
                    options='-vn'
                )
            )

            await asyncio.sleep(play_item.length)

            while vc.is_playing():  # Additional check if the bot is still playing.
                await asyncio.sleep(1)

        self.expired = True

    @staticmethod
    async def _send_embed(play_item: OnlinePlayItem) -> None:
        """
        Internal method for creating and sending an embed. Sent when a song starts playing.

        :param play_item: PlayItem
        :return: None
        """
        message = play_item.message
        embed = Embed(
            title='Now Playing',
            description=f'[{play_item.title}]({play_item.video_url})'
        )
        embed.set_thumbnail(url=play_item.thumbnail)
        embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)

        await message.channel.send(embed=embed)

    async def recreate_player_task(self) -> None:
        """
        Method used for recreating the player task. When called, it stops playing the song, afterwards it stops the
        asyncio FFMPEG task and finally recreates it. This is useful when the player has to be stopped or the current
        song has to be skipped.

        :return: None
        """
        vc: Union[VoiceClient, None] = self.guild.voice_client
        vc.stop()
        self.task.cancel()
        self.task = asyncio.create_task(self.play_in_channel())

    async def pause(self) -> None:
        """
        Simple method for pausing the voice client.

        :return: None
        """
        vc: Union[VoiceClient, None] = self.guild.voice_client

        if not vc.is_paused():
            vc.pause()

    async def resume(self) -> None:
        """
        Simple method for resuming the voice client.

        :return: None
        """
        vc: Union[VoiceClient, None] = self.guild.voice_client

        if vc.is_paused():
            vc.resume()
