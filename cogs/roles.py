import discord
from discord.ext import commands, tasks
import asyncio
import loadconfig
import logging

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.read_config.start()
        self.config_file = "config.json"
        logging.basicConfig(filename="bot.log", level=logging.INFO)

    @tasks.loop(minutes=5.0)
    async def read_config(self):
        config = loadconfig.read("roles")
        self.mod_list = config["mod_list"]
        self.mod_role = config["mod_role"]
        self.normal_role = config["normal_role"]

    def cog_unload(self):
        self.read_config.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.id in self.mod_list:
            rank = discord.utils.get(member.guild.roles, name=self.mod_role)
        else:
            rank = discord.utils.get(member.guild.roles, name=self.normal_role)
        await member.add_roles(rank)
        logging.info(f"{member} was given the {rank} role.")

def setup(bot):
    bot.add_cog(Roles(bot))
