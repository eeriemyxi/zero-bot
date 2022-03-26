from __future__ import annotations

from ast import literal_eval
from asyncio import sleep
from os import environ
from typing import TYPE_CHECKING
from contextlib import suppress

import disnake
from disnake.ext import commands

if TYPE_CHECKING:
    from bot import ZeroBot


class FlagMessageView(disnake.ui.View):
    def __init__(self, message: disnake.Message, bot: ZeroBot):
        super().__init__(timeout=None)
        self.stop_is_pressed: bool = False
        self.message = message
        self.bot = bot

        self.add_item(disnake.ui.Button(label="Go to message", style=disnake.ButtonStyle.link, url=self.message.jump_url))

    @disnake.ui.button(label="Stop alarm", style=disnake.ButtonStyle.danger, emoji="🛑")
    async def stop_button(
        self, btn: disnake.ui.Button, inter: disnake.CommandInteraction
    ):
        await inter.response.defer()

        if inter.author.guild_permissions.moderate_members:
            self.stop_is_pressed = True
            await inter.followup.send("Alarm stopped.")
        else:
            await inter.followup.send("You need `moderate members` permission to stop the alarm.", ephemeral=True)


class MessageFilter(commands.Cog):
    def __init__(self, bot: ZeroBot):
        self.bot = bot
        self.authors: list[int] = literal_eval(environ["FILTER_AUTHORS"])
        self.prefixes: list[str] = literal_eval(environ["FILTER_PREFIXES"])
        self.channels: list[int] = literal_eval(environ["FILTER_CHANNELS"])
        self.whitelist: list[str] = literal_eval(environ["FILTER_WHITELIST_MESSAGES"])
        self.toggle: bool = literal_eval(environ["FILTER_TOGGLE"])
        self.seconds: int = literal_eval(environ["FILTER_SECONDS"])

        if not self.toggle:
            self.bot.remove_listener(self.prefix_filter)

    def parse_message_content(self, msg: disnake.Message) -> str:
        embed = msg.embeds

        if embed:
            embed = embed[0].to_dict()
            cont = msg.content, embed.get("title", ""), embed.get("description", "")
        else:
            cont = [msg.content]

        return "\n".join(map(str.lower, cont))

    @commands.Cog.listener(name="on_message")
    async def prefix_filter(self, msg: disnake.Message):
        if msg.channel.id in self.channels:
            if any(
                cont.lower() in self.parse_message_content(msg)
                for cont in self.whitelist
            ):
                return

            if msg.author.id in self.authors:
                await sleep(self.seconds)
                await msg.delete()

            if msg.content.startswith(self.prefixes):
                await msg.delete()

    @commands.slash_command()
    async def flag(self, inter: disnake.CommandInteraction):
        pass

    @flag.sub_command()
    async def set_channel(
        self, inter: disnake.CommandInteraction, flag_channel: disnake.TextChannel
    ):
        """
        Set the channel where flagged message alarms will be sent.

        Parameters
        ----------
        flag_channel: `disnake.TextChannel`
            The channel.
        """
        if not await self.bot.db.get("message_flagging"):
            await self.bot.db.put(
                dict(flag_channel=str(flag_channel.id)), "message_flagging"
            )
        else:
            await self.bot.db.update(
                dict(flag_channel=str(flag_channel.id)), "message_flagging"
            )

        await inter.send("Channel set.")

    @flag.sub_command()
    async def message(self, inter: disnake.CommandInteraction, message: disnake.Message):
        """
        Flag a message using its message ID.

        Parameters
        ----------
        message: `disnake.Message`
            Message ID.
        """
        await inter.response.defer(ephemeral=True)
    
        filtering = await self.bot.db.get("message_flagging")
        flag_channel_id = int(filtering["flag_channel"])
        flag_channel = self.bot.get_channel(flag_channel_id)
        flag_view = FlagMessageView(message=message, bot=self.bot)

        embed = disnake.Embed(title="⚠️ Alarm")
        embed.add_field(name="Message Flagged By", value=f"{inter.author.mention}", inline=False)
        embed.add_field(name="Message Information", value=f"Creation time: {disnake.utils.format_dt(message.created_at, style='F')}\nAuthor: {message.author.mention}")
        embed.add_field(name="Message Content", value=f"{message.content}", inline=False)

        await inter.followup.send("Message has been flagged.", ephemeral=True)

        while not flag_view.stop_is_pressed:
            msg = await flag_channel.send(content="@everyone", embed=embed, view=flag_view)
            await sleep(2.0)
            await msg.delete()

        with suppress(Exception):
            await msg.delete()