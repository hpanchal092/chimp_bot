import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import datetime


class NoNutNovember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.failed_list = set()
        self.not_failed_list = set()
        self.counter = 0

    @tasks.loop(hours=24.0)
    async def send_nnn_query(self):
        members = self.nnn_channel.guild.members
        for user in members:
            if user not in self.not_failed_list and user.bot is False:
                self.failed_list.add(user)
        self.not_failed_list = set()
        self.counter += 1

        embed = discord.Embed(title=f"Daily NNN Query - Day {self.counter}")
        embed.add_field(name="Today is", value=f"{datetime.date.today()}")
        embed.add_field(name="Did you 🥜 yesterday?", value="Yes 🥜 or No 😎?")

        acc = ""
        for user in self.failed_list:
            acc += f"<@!{user.id}>, "

        async def clear(interaction: discord.Interaction):
            user = interaction.user
            if (user in self.failed_list):
                await interaction.response.send_message(
                    "you already failed goofy ass mf",
                    ephemeral=True
                )
                return

            self.not_failed_list.add(user)
            await interaction.response.send_message(
                "Marking that you did not 🥜 today.",
                ephemeral=True
            )

        async def fail(interaction: discord.Interaction):
            user = interaction.user
            if user in self.not_failed_list:
                self.not_failed_list.remove(user)
            self.failed_list.add(user)
            await interaction.response.send_message(
                "Marking you as PERMANENTLY failed",
                ephemeral=True
            )

        async def send_confirmation(interaction: discord.Interaction):
            user = interaction.user
            if (user in self.failed_list):
                await interaction.response.send_message(
                    "you already failed goofy ass mf",
                    ephemeral=True
                )
                return

            confirm = Button(label="yea", emoji="😭")
            confirm.callback = fail
            confirm_view = View(timeout=None)
            confirm_view.add_item(confirm)
            await interaction.response.send_message(
                "Are you sure?",
                ephemeral=True,
                view=confirm_view
            )

        pass_button = Button(emoji="😎", style=discord.ButtonStyle.green)
        pass_button.callback = clear

        fail_button = Button(style=discord.ButtonStyle.red, emoji="🥜")
        fail_button.callback = send_confirmation

        view = View(timeout=None)
        view.add_item(pass_button)
        view.add_item(fail_button)

        await self.nnn_channel.send(
            f"@everyone, Everyone who failed so far:\n{acc}\n",
            view=view,
            embed=embed
        )

    @commands.command()
    async def send_failed_list(self, ctx):
        acc = ""
        for user in self.failed_list:
            acc += f"{user.display_name}, "
        await ctx.send(f"Failed: {acc}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def remove_failed_user(self, ctx, user: discord.Member):
        self.failed_list.remove(user)
        await ctx.send("👍")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def start_nnn_query(self, ctx):
        self.nnn_channel = discord.utils.get(ctx.guild.channels, name="nnn")
        for user in ctx.guild.members:
            self.not_failed_list.add(user)
        self.send_nnn_query.start()


async def setup(bot):
    await bot.add_cog(NoNutNovember(bot))
