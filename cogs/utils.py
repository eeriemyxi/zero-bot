import disnake
from disnake.ext import commands
from ext.utils import send_message, parse_env_data
from os import environ
from contextlib import suppress


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokens = parse_env_data(environ.get("USER_TOKENS"))
    
    @commands.command(aliases=["up"])
    async def userphone(self, ctx):
        with suppress(Exception):
            await send_message(ctx.bot.session, ctx.channel.id, self.tokens["dankruptbest"], "--userphone")
    
    @commands.is_owner()
    @commands.command()
    async def send(self, ctx, user: str, *, content: str):
        for username in self.tokens:
            if username.startswith(user):
                with suppress(Exception):
                    await send_message(self.bot.session, ctx.channel.id, self.tokens[username], content)