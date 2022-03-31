import threading
import time
from asyncio import sleep
from collections import UserList
from contextlib import suppress
from dataclasses import dataclass
from os import environ

import disnake
from disnake.ext import commands
from ext.constants import PREFIXES
from ext.utils import parse_env_data, send_message


@dataclass
class ActiveLoggingMessage:
    author: int
    time: float


class ActiveUserLogging(UserList):
    def __init__(self, expiry_time: int):
        super().__init__(self)
        self.data: list[ActiveLoggingMessage]
        self.expiry = expiry_time

    def __contains__(self, msg: disnake.Message) -> bool:
        for m in self.data:
            if msg.author.id == m.author:
                return True

        return False

    def add_user(self, msg: disnake.Message):
        log_msg = ActiveLoggingMessage(
            author=msg.author.id, time=int(msg.created_at.timestamp())
        )

        if msg not in self:
            super().append(log_msg)
        else:
            for i, x in enumerate(self.data.copy()):
                if x.author == log_msg.author:
                    del self.data[i]
            super().append(log_msg)

        threading.Thread(None, self.expire, args=[log_msg]).start()

    def expire(self, msg: ActiveLoggingMessage):
        before_time = msg.time
        time.sleep(self.expiry)

        for i, m in enumerate(self.data):
            if msg.author == m.author and before_time <= m.time:
                del self.data[i]

    def get_users_for(self, seconds: int):
        for user in self.data:
            if time.time() - user.time <= seconds:
                yield user.author


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokens = parse_env_data(environ.get("USER_TOKENS"))
        self.active_users = ActiveUserLogging(expiry_time=18000)

    @commands.is_owner()
    @commands.command()
    async def send(self, ctx: commands.Context, user: str, *, content: str):
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
                        await ctx.channel.purge(
                            check=lambda msg: eval(
                                " ".join(args), dict(msg=msg, cont=msg.content)
                            ),
                            limit=amount,
                        )
                else:
                    await ctx.send(
                        "You don't have permission to run this mode. Only the bot owner is allowed to use this mode."
                    )

        with suppress(Exception):
            await ctx.message.delete()

    @commands.Cog.listener("on_message")
    async def logging(self, msg: disnake.Message):
        if not msg.author.bot:
            self.active_users.add_user(msg)

    @commands.slash_command()
    async def ping(
        self,
        inter: disnake.CommandInteraction,
        hours: int = commands.Param(
            choices={f"{x} hour(s) to present": x for x in range(1, 6)}
        ),
    ):
        """Pings all the users who sent messages in a period of time.

        Parameters
        ----------
        hours: The period of time.
        """
        await inter.send(
            content=", ".join(
                f"<@{x}>" for x in self.active_users.get_users_for(3600 * hours)
            )
            or "No users recorded yet, perhaps, it's because the chat has been dead for 5 hours?"
        )
