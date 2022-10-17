from discord.ext import commands


class BaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"{round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def echo(self, ctx, *, arg):
        await ctx.send(arg)


async def setup(bot):
    await bot.add_cog(BaseCommands(bot))
