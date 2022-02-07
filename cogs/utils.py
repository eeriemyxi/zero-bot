from asyncio import sleep
from contextlib import suppress
from os import environ

import disnake
from disnake.ext import commands
from ext.utils import parse_env_data, send_message


PREFIXES = (
    "!",
    "#",
    "$",
    "%",
    "&",
    "(",
    ")",
    "+",
    ",",
    "-",
    ".",
    "/",
    ";",
    "=",
    ">",
    "?",
    "[",
    "]",
    "^",
    "{",
    "|",
    "}",
    "~",
    "₹",
    "ch!",
    "m!",
    "s.",
    "bday",
    "pls",
    "owo",
)


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
                    await send_message(
                        self.bot.session, ctx.channel.id, self.tokens[username], content
                    )
                    await sleep(1)
            return

        for username in self.tokens:
            if username.startswith(user.lower()):
                with suppress(Exception):
                    await send_message(
                        self.bot.session, ctx.channel.id, self.tokens[username], content
                    )

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def expel(self, ctx: commands.Context, mode: str, amount: int = 100, *args):
        if amount <= 0:
            amount = 100

        match mode:
            case "bots" | "bot":
                await ctx.channel.purge(check=lambda msg: msg.author.bot)
            case "commands" | "cmd" | "cmds":
                await ctx.channel.purge(
                    check=lambda msg: msg.content.lower().startswith(PREFIXES),
                    limit=amount,
                )
            case "bot&cmds" | "bot&cmd" | "b&c" | "bc":
                await ctx.channel.purge(
                    check=lambda msg: msg.content.lower().startswith(PREFIXES)
                    or msg.author.bot,
                    limit=amount,
                )
            case "self":
                await ctx.channel.purge(
                    check=lambda msg: msg.author == self.bot.user,
                    bulk=False,
                    limit=amount,
                )
            case "py":
                if ctx.author.id == self.bot.owner_id:
                    with suppress(Exception):
                        await ctx.channel.purge(check=lambda msg: eval(" ".join(args), dict(msg=msg, cont=msg.content)), limit=amount)
                else:
                    await ctx.send("You don't have permission to run this mode. Only the bot owner is allowed to use this mode.")

        with suppress(Exception):
            await ctx.message.delete()
