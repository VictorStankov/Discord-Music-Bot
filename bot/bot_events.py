from discord import Permissions, Member, VoiceState
from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import oauth_url

from bot.model.music_controller import MusicController


class BotEvents(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Method that prints an invitation URL after the bot is loaded.

        :return: None
        """
        perms = ['read_messages', 'send_messages', 'embed_links', 'read_message_history', 'add_reactions', 'connect',
                 'speak', 'use_voice_activation']
        a = Permissions()
        for perm in perms:  # Probably there's a prettier way of doing this.
            a.__setattr__(perm, True)
        print(oauth_url(client_id=self.client.application_id, permissions=a))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
        """
        Method that gets triggered every time someone leaves/enters a channel. It checks whether a user has disconnected
        and the bot is left alone in a channel. If so, it disconnects it automatically.

        :param member: Member who changed their voice state
        :param before: Voice state before the change
        :param after: Voice state after the change
        :return: None
        """

        # member.guild.voice_client returns either the channel the bot is connected in the particular server or None.
        if member.guild.voice_client:
            # Check if the user left the channel that the bot is currently in and whether the bot is alone.
            if before.channel == member.guild.voice_client.channel and len(before.channel.members) == 1:
                await MusicController.destroy_player_vc(vc=before.channel)
                await member.guild.voice_client.disconnect(force=False)
