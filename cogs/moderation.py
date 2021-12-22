import discord
from discord.ext import commands, tasks
import asyncio
import loadconfig
import logging
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kick_words_file = ""
        self.votekick_requirement = None
        self.read_config.start()
        self.update_kick_words.start()
        logging.basicConfig(filename="bot.log", level=logging.INFO)

    @tasks.loop(minutes=5.0)
    async def read_config(self):
        config = loadconfig.read("moderation")
        self.kick_words_file = config["kick_words_file"]
        self.kick_message = config["kick_message"]
        self.votekick_requirement = config["votekick_requirement"]

    @tasks.loop(minutes=5.0)
    async def update_kick_words(self):
        with open(self.kick_words_file) as f:
            self.kickable_words = f.read().splitlines()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def showwords(self, ctx):
        await ctx.send(str(self.kickable_words))

    def cog_unload(self):
        self.update_kick_words.cancel()
        self.read_config.cancel()

    @commands.command()
    async def updatewords(self, ctx):
        self.update_kick_words.restart()
        await ctx.send("Updated kickable words")

    def check_word(self, word_list: list, text: str):
        lst = []
        for word in word_list:
            if word in text.lower():
                lst.append(word)
        return lst

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user:
            lst = self.check_word(self.kickable_words, message.content)
            for word in lst:
                try:
                    await message.author.kick(reason=f"Sent the word {word}")
                    channel = message.channel
                    await channel.send(self.kick_message)
                    logging.info(f"Kicked user {message.author} for sending {word}")
                except discord.Forbidden:
                    logging.info(f"Insufficent Permissions to kick {message.author}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author != self.bot.user:
            lst = self.check_word(self.kickable_words, after.content)
            for word in lst:
                try:
                    await after.author.kick(reason=f"Sent the word {word},")
                    channel = after.channel
                    await channel.send(self.kick_message)
                    logging.info(f"Kicked user {after.author} for editing message {before.content} to {after.content}")
                except discord.Forbidden:
                    logging.info(f"Insufficent Permissions to kick {after.author}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MaxConcurrencyReached):
            await ctx.channel.send("BE PATIENT YOU PRICK")
            return
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("YOU JUST TRIED TO USE THAT COMMAND, DON'T YOU HAVE SOME PATIENCE?")
            return

    @commands.command()
    async def silence(self, ctx, member: discord.Member=None):
        if not member:
            await ctx.send("Please specify a member")
            return

        msg = await ctx.send(f"Timeout user {member} for 60 seconds?")
        await msg.add_reaction('✅')

        while True:
            def check(reaction, user):
                return user != self.bot.user and str(reaction.emoji) == '✅' and reaction.message == msg
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                await ctx.send(f"Insufficient votes after 30 seconds, {member} was not timed out")
                return
            else:
                if reaction.count > self.votekick_requirement:
                    try:
                        time = discord.utils.utcnow() + timedelta(minutes=1)
                        await member.timeout(time)
                        logging.info(f"Silencing user {member}")
                        await ctx.send(f"Silencing user {member}")
                        return
                    except discord.Forbidden:
                        await ctx.send(f"Insufficent permissions to silence {member}")
                        logging.info(f"Insufficent permissions to silence {member}")
                        return

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def votekick(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Please specify a member")
            return

        msg = await ctx.send(f"Kick user {member}?")
        await msg.add_reaction('✅')

        while True:
            def check(reaction, user):
                return user != self.bot.user and str(reaction.emoji) == '✅' and reaction.message == msg
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                await ctx.send(f"Insufficient votes after 30 seconds, {member} was not kicked")
                return
            else:
                print(reaction.count)
                if reaction.count > self.votekick_requirement:
                    try:
                        await member.kick(reason="Votekicked")
                        logging.info(f"Kicking user {member} due to votekick")
                        await ctx.send(f"Kicking user {member}")
                        await ctx.send(self.kick_message)
                        return
                    except discord.Forbidden:
                        await ctx.send(f"Insufficent permissions to kick {member}")
                        logging.info(f"Insufficent permissions to kick {member}")
                        return

def setup(bot):
    bot.add_cog(Moderation(bot))
