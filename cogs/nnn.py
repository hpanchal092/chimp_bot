import discord
from discord.ext import commands, tasks
import asyncio
import datetime

class NoNutNovember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.failed_list = []

    @tasks.loop(hours=24.0)
    async def send_nnn_query(self):
        embed=discord.Embed(title="Daily NNN Query", color=0xff0059)
        embed.add_field(name="Today is", value=f"{datetime.date.today()}")
        embed.add_field(name=f"Did you 🥜 yesterday?", value="Yes or No?")

        acc = ""
        for user in self.failed_list:
            acc += user
            user += "\n"

        await self.nnn_channel.send(f"@everyone, Everyone who failed so far: \n\n {acc}")
        msg = await self.nnn_channel.send(embed=embed)
        for emoji in ("❎", "✅"):
            await msg.add_reaction(emoji)

        passed = []
        while True:
            def check(reaction, user):
                return str(reaction.emoji) in ("❎", "✅") and reaction.message == msg and user != self.bot.user
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=86400, check=check)
            except asyncio.TimeoutError:
                for user in ctx.guild.members.id:
                    if user not in passed:
                        self.failed_list.append(user)
                return
            else:
                if str(reaction.emoji) == "✅":
                    msg = await self.nnn_channel.send(f"<@!{user.id}>, are you sure you failed No Nut November??")
                    await msg.add_reaction("✅")

                    while True:
                        def check(reaction, user):
                            return str(reaction.emoji) == "✅" and reaction.message == msg and reaction.message.author == self.bot.get_user(reaction.message.author.id)
                        try:
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
                        except asyncio.TimeoutError:
                            await ctx.send("Timed Out")
                            return
                        else:
                            self.failed_list.append("<@!" + str(reaction.message.author.id) + ">")
                            await self.nnn_channel.send("You have permanently failed No Nut November")
                            return


    @commands.command(hidden=True)
    @commands.is_owner()
    async def remove_failed_user(self, ctx, member: discord.Member):
        member_id = member.id
        self.failed_list.remove(member_id)
        await ctx.send("👍")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def start_nnn_query(self, ctx):
        self.send_nnn_query.stop()
        self.send_nnn_query.start()
        self.nnn_channel = discord.utils.get(ctx.guild.channels, name="nnn")

def setup(bot):
    bot.add_cog(NoNutNovember(bot))
