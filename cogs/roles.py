import discord
from discord.ext import commands, tasks
import loadconfig
import logging


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "config.json"
        logging.basicConfig(filename="bot.log", level=logging.INFO)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def otherforcestart(self, ctx):
        self.read_config.start()

    @tasks.loop(minutes=5.0)
    async def read_config(self):
        config = loadconfig.read("roles")
        self.mod_list = config["mod_list"]
        self.mod_role = config["mod_role"]
        self.normal_role = config["normal_role"]

    def cog_unload(self):
        self.read_config.cancel()

    def cog_load(self):
        self.read_config.start()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.id in self.mod_list:
            rank = discord.utils.get(member.guild.roles, name=self.mod_role)
        else:
            rank = discord.utils.get(member.guild.roles, name=self.normal_role)
        await member.add_roles(rank)
        logging.info(f"{member} was given the {rank} role.")


async def setup(bot):
    await bot.add_cog(Roles(bot))
