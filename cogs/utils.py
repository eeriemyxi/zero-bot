from asyncio import sleep
from contextlib import suppress
from os import environ

import disnake
from disnake.ext import commands
from ext.utils import parse_env_data, send_message


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokens = parse_env_data(environ.get("USER_TOKENS"))
    
    @commands.is_owner()
    @commands.command()
    async def send(self, ctx, user: str, *, content: str):
        if user.lower() == "all":
            for username in self.tokens:
                with suppress(Exception):
                    await send_message(self.bot.session, ctx.channel.id, self.tokens[username], content)
                    await sleep(2)
            return

        for username in self.tokens:
            if username.startswith(user.lower()):
                with suppress(Exception):
                    await send_message(self.bot.session, ctx.channel.id, self.tokens[username], content)
