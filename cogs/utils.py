import threading
import time
from asyncio import sleep
from contextlib import suppress
from dataclasses import dataclass, field
from os import environ

import disnake
from disnake.ext import commands
from ext.constants import PREFIXES
from ext.utils import parse_env_data, send_message


@dataclass(unsafe_hash=True)
class ActiveLogMessage:
    time: int = field(compare=False, hash=False)
    author: int = field(compare=True, hash=True)


class ActiveUserLogging:
    def __init__(self, expiry_time: int):
        self.data: set[ActiveLogMessage] = set()
        self.expiry_time = expiry_time

    def add_user(self, msg):
        log_msg = ActiveLogMessage(msg.created_at.timestamp(), msg.author.id)

        self.data.add(log_msg)
        for x in self.data:
            if x == log_msg:
                x.time = log_msg.time
                break

        thread = threading.Thread(None, target=self.expire, args=[log_msg], daemon=True)
        thread.start()
    
    def get_log_msg(self, author: int) -> ActiveLogMessage:
        for log_msg in self.data.copy():
            if log_msg.author == author:
                return log_msg

    def expire(self, log_msg: ActiveLogMessage):
        time.sleep(self.expiry_time)

        for x in self.data.copy(): 
            if (x.author, x.time) == (log_msg.author, log_msg.time):
                self.data.remove(x)

    def get_users_for(self, seconds: int):
        for user in self.data:
            if time.time() - user.time <= seconds:
                yield user.author
    
    def __repr__(self) -> str:
        return repr(self.data)


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokens = parse_env_data(environ.get("USER_TOKENS"))
        self.active_users = dict()

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
            try:
                logs = self.active_users[msg.channel.id]
            except KeyError:
                logs = ActiveUserLogging(18000)
                self.active_users[msg.channel.id] = logs

            logs.add_user(msg)


    @commands.slash_command()
    async def ping(
        self,
        inter: disnake.CommandInteraction,
        channel: disnake.TextChannel,
        hours: int = commands.Param(
            choices={f"{x} hour(s) to present": x for x in range(1, 6)})
    ):
        """Pings all the users who sent messages in a period of time.

        Parameters
        ----------
        hours: The period of time.
        """
        try:
            logs = self.active_users[channel.id]
            await inter.send(
                content=", ".join(
                    f"<@{x}>" for x in logs.get_users_for(3600 * hours)
                )
                or "No users recorded yet, perhaps, it's because the chat has been dead for 5 hours? Or maybe the bot was down."
            )
        except KeyError:
            await inter.send(content="No records for this channel yet.")
