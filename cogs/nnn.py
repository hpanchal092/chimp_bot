import discord
from discord.ext import commands, tasks
import asyncio
import datetime

class NoNutNovember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_nnn_msg = None
        self.failed_list = set()
        self.passed_list = set()

    @tasks.loop(hours=24.0)
    async def send_nnn_query(self):
        members = self.nnn_channel.guild.members
        for user in members:
            if user.id not in self.passed_list:
                self.failed_list.add(f"<@!{user.id}> ")

        self.passed_list = []

        embed=discord.Embed(title="Daily NNN Query", color=0xff0059)
        embed.add_field(name="Today is", value=f"{datetime.date.today()}")
        embed.add_field(name=f"Did you 🥜 yesterday?", value="Yes or No?")

        # send everyone who has failed so far list
        acc = ""
        for user in self.failed_list:
            acc += user
            user += "\n"
        await self.nnn_channel.send(f"@everyone, Everyone who failed so far: \n\n {acc}")
        msg = await self.nnn_channel.send(embed=embed)
        for reaction in ("❎", "✅"):
            await msg.add_reaction(reaction)

        self.current_nnn_msg = msg

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message == self.current_nnn_msg:
            if str(reaction.emoji) in ("❎", "✅") and user != self.bot.user:
                # if you passed
                if str(reaction.emoji) == "❎":
                    self.passed_list.add(user.id)

                # if you clicked that you failed
                elif str(reaction.emoji) == "✅":
                    await self.confirm(user)

    async def confirm(self, user):
        # sends confirmation message
        msg = await self.nnn_channel.send(f"<@!{user.id}>, are you sure you failed No Nut November??")
        await msg.add_reaction("✅")

        while True:
            def check(reaction, conf_user):
                return reaction.message == msg and conf_user == user and str(reaction.emoji) == "✅"
            try:
                reaction, conf_user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await self.nnn_channel.send("Timed out, assuming you did not fail")
                return
            else:
                self.failed_list.add(f"<@!{user.id}> ")
                await self.nnn_channel.send("You have permanently failed No Nut November")
                return

    @commands.command()
    async def send_failed_list(self, ctx):
        await ctx.send(f"Failed: {self.failed_list}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def remove_failed_user(self, ctx, member: discord.Member):
        self.failed_list.remove(f"<@!{member.id}>")
        await ctx.send("👍")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def start_nnn_query(self, ctx):
        self.nnn_channel = discord.utils.get(ctx.guild.channels, name="nnn")
        self.passed_list = ctx.guild.members
        self.send_nnn_query.start()

def setup(bot):
    bot.add_cog(NoNutNovember(bot))
