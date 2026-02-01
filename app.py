import asyncio
import logging

import discord
from discord import Intents

from bot import Bot, BotEvents, BotCommands, token, logging_level, bot_description

intents = Intents.all()
client = Bot(command_prefix='s!', intents=intents, case_insensitive=True)


async def main() -> None:
    async with client:
        await client.add_cog(BotEvents(client=client))
        await client.add_cog(BotCommands(client=client))
        client.activity = discord.Game(bot_description)
        await client.start(token)

logging.basicConfig(level=logging_level)
asyncio.run(main())
