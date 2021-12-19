"""
This one is against the TOS. It uses a different bot's messages because I am lazy.
"""
from os import getenv
from asyncio import sleep
from random import uniform

from disnake.ext import commands


class AutoBump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_bot_id = 735147814878969968
        self.role_id = int(getenv("BUMP_REMINDER_ROLE_ID"))
        self.channel_id = int(getenv("AUTO_BUMP_CHANNEL_ID"))
        self.token = getenv("AUTO_BUMP_USER_TOKEN")
        self.url = "https://canary.discord.com/api/v9/channels/%s/messages"

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.channel.id, message.author.id) == (
            self.channel_id,
            self.reminder_bot_id,
        ):
            if any(self.role_id == role.id for role in message.role_mentions):
                await sleep(uniform(5.0, 10.0))
                await self.bot.session.post(
                    url=self.url % self.channel_id,
                    headers=dict(authorization=self.token),
                    json={"content": "!d bump", "content-type": "application/json"},
                )


def setup(bot):
    bot.add_cog(AutoBump(bot))
