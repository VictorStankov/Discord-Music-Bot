import math
from typing import Dict, Tuple

import validators
from discord import VoiceChannel
from discord.ext.commands import Context
from yt_dlp import YoutubeDL

from bot.model import Player, LocalPlayItem, OnlinePlayItem


class MusicController:
    players: Dict[int, Player] = dict()  # Dictionary that stores Players per servers. The key is the unique server ID.

    @staticmethod
    def _search_video(url: str) -> Tuple[int, str, str, str, str]:
        """
        Internal method that finds a video based on the provided argument. If `url` is an actual URL, it proceeds
        directly with retrieving its information. If `url` contains search keywords, it utilises `ytsearch` which
        queries YouTube for the best possible matches and retrieves the first one's information.

        :param url: String - May contain a direct URL or search keywords
        :return: (Length of Video, Download URL, Title, Thumbnail URL, Original URL)
        """
        yt = YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True', 'quiet': 'True'})

        if not validators.url(url):
            data = yt.extract_info(f'ytsearch1:{url}', download=False)['entries'][0]
        else:
            data = yt.extract_info(url, download=False)

        return math.ceil(data['duration']), data['url'], data['title'], data['thumbnail'], data['webpage_url']

    @staticmethod
    async def _get_play_item(ctx: Context, url: str) -> OnlinePlayItem:
        """
        Internal method used for creating a PlayItem object with data provided by `_search_video`.

        :param ctx: Context
        :param url: String - May contain a direct URL or search keywords
        :return: PlayItem
        """
        return OnlinePlayItem(ctx.message, *MusicController._search_video(url=url))

    @classmethod
    async def add_to_queue(cls, ctx: Context, url: str) -> None:
        """
        Core method for adding playing songs. First it retrieves a PlayItem object using `_get_play_item`. After that it
        checks whether a non-expired Player object already exists in the `players` dictionary.

        If so, that means that the Player for this server is still running, and it only adds the PlayItem in its queue.

        Otherwise, it creates a new Player object and saves it in the `players` dictionary.

        :param ctx: Context
        :param url: String - May contain a direct URL or search keywords
        :return: None
        """
        play_item = await MusicController._get_play_item(ctx=ctx, url=url)

        if ctx.guild.id not in cls.players.keys() or cls.players[ctx.guild.id].expired:
            cls.players[ctx.guild.id] = Player(
                guild=ctx.guild,
                play_item=play_item
            )
        else:
            cls.players[ctx.guild.id].queue.append(play_item)

    @classmethod
    async def play_intro_song(cls, ctx: Context):
        """
        Complementary method to the bot's `join` command. It creates a PlayItem object which has its `internal`
        attribute set to True. This means that the source for this object is local. The length and the music path are
        hardcoded. It does not have the same checks as `add_to_queue` since it should only be used when the bot is not
        connected to any channels in the server. These checks are done in the `join` command.

        :param ctx: Context
        :return: None
        """
        play_item = LocalPlayItem(message=ctx.message, length=39, path='./misc/slavi.wav')

        cls.players[ctx.guild.id] = Player(
            guild=ctx.guild,
            play_item=play_item
        )

    @classmethod
    async def destroy_player(cls, ctx: Context) -> None:
        """
        Method for destroying a Player object saved in `players` dictionary. Used for when the bot is leaving a channel.

        :param ctx: Context
        :return: None
        """
        if ctx.guild.id not in cls.players.keys():
            return

        player = cls.players[ctx.guild.id]
        player.task.cancel()
        del cls.players[ctx.guild.id]

    @classmethod
    async def destroy_player_vc(cls, vc: VoiceChannel) -> None:
        """
        Method for destroying a Player object saved in `players` dictionary. Almost identical to `destroy_player` but
        with a different argument. Used by `BotEvents.on_voice_state_update` since there we receive a VoiceState object.

        :param vc: VoiceChannel
        :return: None
        """
        if vc.guild.id not in cls.players.keys():
            return

        player = cls.players[vc.guild.id]
        player.task.cancel()
        del cls.players[vc.guild.id]

    @classmethod
    async def stop_playing(cls, ctx: Context):
        """
        Method for stopping the music and clearing the queue of a Player object.

        :param ctx: Context
        :return: None
        """
        if ctx.guild.id not in cls.players.keys():
            return

        player = cls.players[ctx.guild.id]
        player.queue.clear()
        await player.recreate_player_task()

    @classmethod
    async def clear_queue(cls, ctx: Context) -> None:
        """
        Method for clearing the queue without stopping the currently playing music.

        :param ctx: Context
        :return: None
        """
        if ctx.guild.id not in cls.players.keys():
            return

        cls.players[ctx.guild.id].queue.clear()

    @classmethod
    async def skip_song(cls, ctx: Context) -> None:
        """
        Method for skipping the currently playing song.

        :param ctx: Context
        :return: None
        """
        if ctx.guild.id not in cls.players.keys():
            return

        await cls.players[ctx.guild.id].recreate_player_task()

    @classmethod
    async def pause_player(cls, ctx: Context) -> None:
        """
        Method for pausing the currently playing song.

        :param ctx: Context
        :return: None
        """
        if ctx.guild.id not in cls.players.keys():
            return

        await cls.players[ctx.guild.id].pause()

    @classmethod
    async def resume_player(cls, ctx: Context) -> None:
        """
        Method for resuming the previously playing song.

        :param ctx: Context
        :return: None
        """
        if ctx.guild.id not in cls.players.keys():
            return

        await cls.players[ctx.guild.id].resume()
