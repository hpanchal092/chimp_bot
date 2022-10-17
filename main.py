import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import secret
import logging

intents = discord.Intents.all()
intents.members = True
logging.basicConfig(filename="bot.log", level=logging.INFO)

client = commands.Bot(command_prefix="+c ", intents=intents)

initial_extensions = [
    "cogs.basecommands",
    "cogs.roles",
    "cogs.moderation",
    "cogs.owner",
]


async def load():
    for extension in initial_extensions:
        await client.load_extension(extension)

if __name__ == '__main__':
    asyncio.run(load())


@client.event
async def on_ready():
    now = datetime.now()
    logging.info(f"Bot is online at {now}")

client.run(secret.TOKEN, reconnect=True)
