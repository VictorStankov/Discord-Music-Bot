from typing import Union

from discord import VoiceClient
from discord.ext import commands
from discord.ext.commands import Bot, Context

from bot.model.music_controller import MusicController
from bot import command_descriptions


class BotCommands(commands.Cog):
    """
    Class to encapsulate all commands that users can call.
    """
    def __init__(self, client: Bot):
        self.client = client

    @staticmethod
    async def _get_voice_channel(ctx: Context) -> Union[VoiceClient, None]:
        """
        Static method to retrieve the channel the bot is currently in. If it is not joined in any channel, it tries to
        connect to the caller's channel.

        :param ctx: Context
        :return: VoiceClient, None
        """
        channel: Union[VoiceClient, None] = ctx.guild.voice_client

        if channel is not None and channel.is_connected() is True:
            return channel
        elif ctx.author.voice is not None:
            return await ctx.author.voice.channel.connect(self_deaf=True)
        return None

    @commands.command(brief=command_descriptions.get('join'))
    async def join(self, ctx: Context) -> None:
        """
        Command that makes the bot join the user's channel and play the iconic theme song. It makes checks whether it
        has already joined a channel or the user is not present in any voice channels.

        :param ctx: Context
        :return: None
        """
        if ctx.guild.voice_client:
            await ctx.reply("I'm already connected! :rage:")
            return

        vc = await BotCommands._get_voice_channel(ctx=ctx)

        if not vc:
            await ctx.reply("Voice channel not found! :angry:")
            return

        await MusicController.play_intro_song(ctx=ctx)

    @commands.command(brief=command_descriptions.get('play'))
    async def play(self, ctx: Context, *args) -> None:
        """
        Similar to `join` method. If the bot has not already joined, it joins the user's channel. After that it hands
        the control over to MusicController to start the music clip. After successfully executing, it reacts with a
        checkmark to show the user their request has been serviced.

        :param ctx: Context
        :param args: Music info - can be URL or title of the song
        :return: None
        """
        vc = await BotCommands._get_voice_channel(ctx=ctx)

        if not vc:
            await ctx.reply("Voice channel not found! :angry:")
            return

        await MusicController.add_to_queue(ctx, ' '.join(args))
        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command(brief=command_descriptions.get('leave'), aliases=['dc', 'disconnect'])
    async def leave(self, ctx: Context) -> None:
        """
        Method used for leaving the voice channel. It checks whether the bot is present in any of the voice channels and
        tells MusicController to proceed with destroying the player for the channel.

        :param ctx: Context
        :return: None
        """
        if ctx.guild.voice_client:
            await MusicController.destroy_player(ctx=ctx)
            await ctx.guild.voice_client.disconnect(force=False)
            await ctx.message.add_reaction('\N{WAVING HAND SIGN}')
        else:
            await ctx.reply("I'm not even connected! :triumph:")

    @commands.command(brief=command_descriptions.get('stop'))
    async def stop(self, ctx: Context) -> None:
        """
        Method used for stopping the music player. It checks whether the bot is present in any of the voice channels and
        tells MusicController to proceed with killing the process of the player and clearing its queue.

        :param ctx: Context
        :return: None
        """
        if ctx.guild.voice_client:
            await MusicController.stop_playing(ctx=ctx)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        else:
            await ctx.reply("I'm not even connected! :triumph:")

    @commands.command(brief=command_descriptions.get('clear'))
    async def clear(self, ctx: Context) -> None:
        """
        Method used for clearing the queue of the music player. It checks whether the bot is present in any of the voice
        channels and tells MusicController to proceed with clearing the queue.
        :param ctx: Context
        :return: None
        """
        if ctx.guild.voice_client:
            await MusicController.clear_queue(ctx=ctx)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        else:
            await ctx.reply("I'm not even connected! :triumph:")

    @commands.command(brief=command_descriptions.get('skip'))
    async def skip(self, ctx: Context) -> None:
        """
        Method used for skipping the current playing song. It checks whether the bot is present in any of the voice
        channels and tells MusicController to proceed with skipping the song.
        :param ctx: Context
        :return: None
        """
        if ctx.guild.voice_client:
            await MusicController.skip_song(ctx=ctx)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        else:
            await ctx.reply("I'm not even connected! :triumph:")

    @commands.command(brief=command_descriptions.get('pause'))
    async def pause(self, ctx: Context) -> None:
        """
        Method used for pausing the current playing song. It checks whether the bot is present in any of the voice
        channels and tells MusicController to proceed with pausing the song.
        :param ctx: Context
        :return: None
        """
        if ctx.guild.voice_client:
            await MusicController.pause_player(ctx=ctx)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        else:
            await ctx.reply("I'm not even connected! :triumph:")

    @commands.command(brief=command_descriptions.get('resume'))
    async def resume(self, ctx: Context) -> None:
        """
        Method used for resuming a song if it has been paused. It checks whether the bot is present in any of the voice
        channels and tells MusicController to proceed with resuming the song.
        :param ctx: Context
        :return: None
        """
        if ctx.guild.voice_client:
            await MusicController.resume_player(ctx=ctx)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        else:
            await ctx.reply("I'm not even connected! :triumph:")
