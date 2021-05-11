import discord
from discord.ext import commands, tasks
import asyncio
import json

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kick_words_file = ""
        self.read_config.start()
        self.update_kick_words.start()
        self.config_file = "config.json"

    @tasks.loop(minutes=5.0)
    async def read_config(self):
        with open(self.config_file) as config_file:
            loaded_file = json.load(config_file)
            moderation = loaded_file["moderation"]
            self.kick_words_file = moderation["kick_words_file"]
            self.kick_message = moderation["kick_message"]

    @tasks.loop(minutes=5.0)
    async def update_kick_words(self):
        with open(self.kick_words_file) as f:
            self.kickable_words = f.read().splitlines()

    @commands.command()
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
                    print(f"Kicked user {message.author} for sending {word}")
                except discord.Forbidden:
                    print(f"Insufficent Permissions to kick {message.author}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author != self.bot.user:
            lst = self.check_word(self.kickable_words, after.content)
            for word in lst:
                try:
                    await after.author.kick(reason=f"Sent the word {word},")
                    channel = after.channel
                    await channel.send(self.kick_message)
                    print(f"Kicked user {after.author} for editing message {before.content} to {after.content}")
                except discord.Forbidden:
                    print(f"Insufficent Permissions to kick {message.author}")

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def votekick(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Please specify a member")
            return

        msg = await ctx.send(f"Kick user {member}?")
        await msg.add_reaction('✅')

        votes = 0
        while True:
            def check(reaction, user):
                return user != self.bot.user and str(reaction.emoji) == '✅'
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                await ctx.send(f"Insufficient votes after 30 seconds, {member} was not kicked")
                return
            else:
                votes += 1
                if votes == 3:
                    try:
                        await member.kick(reason="Votekicked")
                        print(f"Kicking user {member} due to votekick")
                        await ctx.send(f"Kicking user {member}")
                        return
                    except discord.Forbidden:
                        await ctx.send(f"Insufficent permissions to kick {member}")
                        print(f"Insufficent permissions to kick {member}")
                        return

def setup(bot):
    bot.add_cog(Moderation(bot))
