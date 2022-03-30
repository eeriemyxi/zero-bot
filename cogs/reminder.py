import asyncio
import time
from contextlib import suppress

import arrow
import disnake
from disnake.ext import commands, tasks


class ReminderMessageView(disnake.ui.View):
    def __init__(self, bot: commands.Bot, cog: commands.Cog):
        super().__init__(timeout=None)
        self.bot = bot
        self.cog = cog
        self.reacted_users: set[int] = set()
        self.rmd_id: str

    @disnake.ui.button(
        label="Remind me",
        emoji="🔔",
        style=disnake.ButtonStyle.green,
        custom_id="remindmebutton",
    )
    async def remind_me(self, _, inter: disnake.MessageInteraction):
        self.reacted_users.add(inter.author.id)

        reminder = await self.bot.reminder_db.get(self.rmd_id)
        if str(inter.author.id) not in reminder["users"]:
            await self.bot.reminder_db.update(
                dict(users=self.bot.reminder_db.util.append(str(inter.author.id))),
                key=self.rmd_id,
            )

        await inter.send(
            content="Okay, I will remind you by sending you a DM or in <#{channel}> if your DMs are off.".format(
                channel=(await self.bot.reminder_db.get("channel"))["value"]
            ),
            ephemeral=True,
        )

    @disnake.ui.button(
        label="View members who are interested",
        emoji="👁‍🗨",
        style=disnake.ButtonStyle.blurple,
        custom_id="viewrmdmemberbutton",
    )
    async def view_members_button(self, _, inter: disnake.MessageInteraction):
        reminder = await self.bot.reminder_db.get(self.rmd_id)
        msg = str()

        for user in reminder["users"]:
            user = self.bot.get_user(int(user))
            msg += user.mention + "\n"

        await inter.send(
            content="List of members:\n" + msg
            if msg
            else "No user is interested for this event yet.",
            ephemeral=True,
        )


class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.load_reminders.start()

    @tasks.loop(count=1)
    async def load_reminders(self):
        reminders = await self.bot.reminder_db.fetch()
        rmd_coros = []

        for reminder in reminders.items:
            rmd = self.load_reminder(reminder)
            rmd_coros.append(rmd)

        await asyncio.gather(*rmd_coros)

    @load_reminders.before_loop
    async def before_loading_reminders(self):
        await self.bot.wait_until_ready()

    async def load_reminder(self, reminder: dict):
        if not reminder["key"] == "channel":
            remaining: int = reminder["time"] - arrow.utcnow().int_timestamp
            print(
                *[f"{x.replace('_', ' ').title()}: {reminder[x]}" for x in reminder],
                sep="\n",
            )
            print(f"Remaining time for {reminder['title']}: {remaining} seconds.\n\n")

            if remaining > 0:
                remind_view = ReminderMessageView(self.bot, self)
                remind_view.rmd_id = reminder["key"]
                self.bot.add_view(remind_view)

                channel = self.bot.get_channel(int(reminder["channel"]))
                msg = await channel.fetch_message(reminder["key"])

                await msg.edit(view=remind_view)
                remaining = await self.anticipate(reminder["key"], remaining)
                await asyncio.sleep(remaining)

            await self.text_users(reminder["key"])

    @commands.slash_command()
    async def publicremind(self, _):
        """
        Let everyone press a button to get reminded about something.
        """

        pass

    @publicremind.sub_command(name="new")
    async def new_reminder(
        self,
        inter: disnake.CommandInteraction,
        title: str,
        message: str,
        _time: str = commands.Param(name="time"),
        ping_role: disnake.Role = None,
    ):
        """
        Set new reminder.

        Parameters
        ----------
        title: This will be the title of the message.
        message: This will be the description of the message about this reminder.
        ping_role: Role to ping, it is optional.
        _time: MMMM DD YYYY HH:mm:ss A | Example: January 01 2022 09:30:45 PM
        """
        await inter.response.defer(ephemeral=True)

        self.remind_view = ReminderMessageView(self.bot, self)
        self.time = arrow.get(
            _time, "MMMM DD YYYY HH:mm:ss A", tzinfo="Asia/Kolkata"
        ).int_timestamp

        reminder_msg = await inter.channel.send(
            content=ping_role.mention if ping_role else str(),
            embed=disnake.Embed(title=title, description=message).add_field(
                name="Time", value=f"<t:{self.time}:F>"
            ),
            view=self.remind_view,
        )
        rmd_id = str(reminder_msg.id)
        self.remind_view.rmd_id = rmd_id
        await self.bot.reminder_db.put(
            dict(
                time=self.time,
                author=str(inter.author.id),
                creation_time=int(time.time()),
                title=title,
                message=message,
                channel=str(inter.channel.id),
                users=[],
            ),
            key=rmd_id,
        )
        await inter.send(content="Message sent.")

        dt = self.time - arrow.utcnow().int_timestamp
        remaining = await self.anticipate(rmd_id, dt)
        await asyncio.sleep(remaining)
        await self.text_users(rmd_id)

    async def text_users(self, rmd_id: str):
        reminder = await self.bot.reminder_db.get(rmd_id)

        for user in reminder["users"]:
            user = self.bot.get_user(int(user))
            embed = disnake.Embed(
                title=reminder["title"],
                description="Hey, {user.mention}!\n<t:{creation}:R> someone in Zero Inc. set a reminder for **{title}**. So I reminded you about it because you asked me to.".format(
                    user=user,
                    creation=reminder["creation_time"],
                    title=reminder["title"],
                ),
            )

            try:
                await user.send(embed=embed)
            except Exception:
                channel_id = await self.bot.reminder_db.get("channel")
                channel = self.bot.get_channel(int(channel_id["value"]))
                with suppress(Exception):
                    await channel.send(content=user.mention, embed=embed)

        channel = self.bot.get_channel(int(reminder["channel"]))
        msg = await channel.fetch_message(reminder["key"])
        await self.bot.reminder_db.delete(rmd_id)
        await msg.edit(view=None)

    async def anticipate(self, rmd_id, time: int):
        if time > 7200:
            await asyncio.sleep(time - 7200)
            reminder = await self.bot.reminder_db.get(rmd_id)
            channel_id = await self.bot.reminder_db.get("channel")

            for user in reminder["users"]:
                user = self.bot.get_user(int(user))
                await self.safe_send(
                    user,
                    self.bot.get_channel(int(channel_id["value"])),
                    "Hey {user.mention}, **{title}** is in 2 hours. Be prepared.".format(
                        user=user, title=reminder["title"]
                    ),
                )
                time = 7200

        if time > 1800:
            await asyncio.sleep(time - 1800)
            reminder = await self.bot.reminder_db.get(rmd_id)
            channel_id = await self.bot.reminder_db.get("channel")

            for user in reminder["users"]:
                user = self.bot.get_user(int(user))
                await self.safe_send(
                    user,
                    self.bot.get_channel(int(channel_id["value"])),
                    "Hey {user.mention}, **{title}** is in 30 minutes. Be prepared.".format(
                        user=user, title=reminder["title"]
                    ),
                )
                time = 1800

        return time

    async def safe_send(
        self,
        user: disnake.User | disnake.Member,
        channel: disnake.TextChannel,
        content: str,
    ):
        """Tries to send a message to the user and if it fails, it will try to send it to the channel."""
        try:
            await user.send(content)
        except Exception:
            with suppress(Exception):
                await channel.send(content)

    @publicremind.sub_command()
    async def set_backup_channel(
        self, inter: disnake.CommandInteraction, channel: disnake.TextChannel
    ):
        """
        If the user has DMs turned off, the user will be reminded in this channel.
        """

        await self.bot.reminder_db.put(str(channel.id), key="channel")
        await inter.send(f"Backup channel has been set to {channel.mention}")
