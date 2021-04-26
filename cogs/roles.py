import discord
from discord.ext import commands, tasks
import asyncio
import json

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.read_config.start()
        self.config_file = "config.json"

    @tasks.loop(minutes=5.0)
    async def read_config(self):
        with open(self.config_file) as config_file:
            loaded_file = json.load(config_file)
            roles = loaded_file["roles"]
            self.mod_list = roles["mod_list"]
            self.mod_role = roles["mod_role"]
            self.normal_role = roles["normal_role"]

    def cog_unload(self):
        self.read_config.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.id in self.mod_list:
            rank = discord.utils.get(member.guild.roles, name=self.mod_role)
        else:
            rank = discord.utils.get(member.guild.roles, name=self.normal_role)
        await member.add_roles(rank)
        print(f"{member} was given the {rank} role.")

def setup(bot):
    bot.add_cog(Roles(bot))
