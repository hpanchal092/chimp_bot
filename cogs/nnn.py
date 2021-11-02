import discord
from discord.ext import commands, tasks
import asyncio
import datetime

class NoNutNovember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.nnn_channel = discord.utils.get(ctx.guild.channels, name="nnn")
        self.failed_list = []

    @tasks.loop(hours=24.0)
    async def send_nnn_query():
        embed=discord.Embed(title="Daily NNN Query", color=0xff0059)
        embed.add_field(name=f"Today is {datetime.date.day}/30", value="")
        embed.add_field(name=f"Did you 🥜 yesterday?", value="")

        await self.nnn_channel.send(f"@everyone, Everyone who failed so far:\n\n{"\n".join(self.failed_list)}")
        msg = await self.nnn_channel.send(embed=embed)
        for emoji in ("❎", "✅"):
            await msg.add_reaction(emoji)

        passed = []
        while True:
            def check(reaction, user):
                return str(reaction.emoji) in ("❎", "✅") and reaction.message == msg
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=86400, check=check)
            except asyncio.TimeoutError:
                for user in ctx.guild.members.id:
                    if user not in passed:
                        self.failed_list.append(user)
                return
            else:
                if str(reaction.emoji) == "✅":
                    confirm_failure(reaction.message.author.id)
                else:
                    passed.append(reaction.message.author.id)


    @commands.command(hidden=True)
    @commands.is_owner()
    async def confirm_failure(user):
        msg = await nnn_channel.send(f"<@!{user}>, are you sure you failed No Nut November??")
        await msg.add_reaction("✅")

        while True:
            def check(reaction, user):
                return str(reaction.emoji) == "✅" and reaction.message == msg and reaction.message.author == bot.get_user(user)
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timed Out")
                return
            else:
                self.failed_list.append("<@!" + str(user) + ">")
                await ctx.send("You have permanently failed No Nut November")
                return

    @commands.command(hidden=True)
    @commands.is_owner()
    async def start_nnn_query():
        self.send_nnn_query.restart()


