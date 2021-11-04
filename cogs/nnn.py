import discord
from discord.ext import commands, tasks
import asyncio
import datetime

class NoNutNovember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.failed_list = []
        self.passed_list = []
        self.TASK_LOOP = 24.0
        self.TASK_LOOP_SEC = self.TASK_LOOP * 60 * 60

    @tasks.loop(hours=24.0)
    async def send_nnn_query(self):
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

        query = asyncio.create_task(self.query(msg))
        await asyncio.sleep(self.TASK_LOOP_SEC)
        query.cancel()

        guild = self.nnn_channel.guild
        for user in guild.members:
            if user not in self.passed_list:
                self.failed_list.append(user)
        return

    async def query(self, msg):
        for emoji in ("❎", "✅"):
            await msg.add_reaction(emoji)

        while True:
            def check(reaction, user):
                return str(reaction.emoji) in ("❎", "✅") and reaction.message == msg and user != self.bot.user

            while True:
                reaction, user = await self.bot.wait_for("reaction_add", check=check)

                # if you passed
                if str(reaction.emoji) == "❎":
                    self.passed_list.append(user)

                # if you clicked that you failed
                elif str(reaction.emoji) == "✅":
                    await self.confirm(user)

    async def confirm(self, user):
        # sends confirmation message
        conf_msg = await self.nnn_channel.send(f"<@!{user.id}>, are you sure you failed No Nut November??")
        await conf_msg.add_reaction("✅")

        while True:
            def check(conf_reaction, conf_user):
                return conf_reaction.message == conf_msg and user == conf_user and str(conf_reaction.emoji) == "✅"
            try:
                conf_reaction, conf_user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await self.nnn_channel.send("Timed out, assuming you did not fail")
                return
            else:
                self.failed_list.append(f"<@!{str(user.id)}>")
                await self.nnn_channel.send("You have permanently failed No Nut November")
                return


    @commands.command()
    async def debug(self, ctx):
        await ctx.send(f"Failed: {self.failed_list}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def remove_failed_user(self, ctx, member: discord.Member):
        self.failed_list.remove(f"<@!{member.id}>")
        await ctx.send("👍")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def start_nnn_query(self, ctx):
        self.send_nnn_query.stop()
        self.send_nnn_query.start()
        self.nnn_channel = discord.utils.get(ctx.guild.channels, name="nnn")

def setup(bot):
    bot.add_cog(NoNutNovember(bot))
