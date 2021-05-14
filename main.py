import discord
from discord.ext import commands
from datetime import datetime
import secret

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="-c ", intents=intents)

initial_extensions = ["cogs.basecommands",
                      "cogs.roles",
                      "cogs.moderation",
                      "cogs.owner"]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    now = datetime.now()
    print("Bot is online at", now)

bot.run(secret.TOKEN)
