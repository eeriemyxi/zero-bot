from disnake.ext import commands
from os import getenv
from ast import literal_eval
from asyncio import sleep


class MessageFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.authors = literal_eval(getenv("FILTER_AUTHORS"))
        self.prefixes = literal_eval(getenv("FILTER_PREFIXES"))
        self.channels = literal_eval(getenv("FILTER_CHANNELS"))
        self.toggle = literal_eval(getenv("FILTER_TOGGLE"))
        self.seconds = literal_eval(getenv("FILTER_SECONDS"))

        if self.toggle is False:
            self.bot.remove_listener(self.on_message)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id in self.channels:
            if msg.author.id in self.authors:
                await sleep(self.seconds)
                await msg.delete()
            if msg.content.startswith(self.prefixes):
                await msg.delete()
