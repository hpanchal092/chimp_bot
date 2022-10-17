from discord.ext import commands


class OwnerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Error loading {cog}\n{type(e).__name__} - {e}")
        else:
            await ctx.send(f"Successfully loaded {cog}")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Error unloading {cog}\n{type(e).__name__} - {e}")
        else:
            await ctx.send(f"Successfully unloaded {cog}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Error reloading {cog}\n{type(e).__name__} - {e}")
        else:
            await ctx.send(f"Successfully reloaded {cog}")


async def setup(bot):
    await bot.add_cog(OwnerCog(bot))
