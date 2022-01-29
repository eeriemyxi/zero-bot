import asyncio
import time
from contextlib import suppress

import disnake
from disnake.ext import commands, tasks


class ReminderMessageView(disnake.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.reacted_users: set[int] = set()

    @disnake.ui.button(
        label="Remind me",
        emoji="🔔",
        style=disnake.ButtonStyle.green,
        custom_id="remindmebutton",
    )
    async def remind_me(self, _, inter: disnake.MessageInteraction):
        self.reacted_users.add(inter.author.id)

        reminder = await self.bot.reminder_db.get(self.db_id)
        if str(inter.author.id) not in reminder["users"]:
            await self.bot.reminder_db.update(
                dict(users=self.bot.reminder_db.util.append(str(inter.author.id))),
                key=self.db_id,
            )

        await inter.send(
            content="Okay, I will remind you by sending you a DM or in <#{channel}> if your DMs are off.".format(
                channel=(await self.bot.reminder_db.get("channel"))["value"]
            ),
            ephemeral=True,
        )


class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.load_reminders.start()

    @tasks.loop(count=1)
    async def load_reminders(self):
        reminders = await self.bot.reminder_db.fetch()

        for reminder in reminders.items:
            if not reminder["key"] == "channel":
                print(reminder)
                remaining = reminder["time"] - time.time()

                if remaining > 0:
                    remind_view = ReminderMessageView(self.bot)
                    remind_view.db_id = reminder["key"]
                    self.bot.add_view(remind_view)

                    channel = self.bot.get_channel(int(reminder["channel"]))
                    msg = await channel.fetch_message(reminder["key"])

                    await msg.edit(view=remind_view)
                    await asyncio.sleep(remaining)

                await self.text_users(reminder["key"], reminder["users"])

    @load_reminders.before_loop
    async def before_loading_reminders(self):
        await self.bot.wait_until_ready()

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
        seconds: int,
        ping_role: disnake.Role = None,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
    ):

        """
        Set new reminder.

        Parameters
        ----------
        title: This will be the title of the message.
        message: This will be the description of the message about this reminder.
        ping_role: Role to ping, it is optional.
        """
        await inter.response.defer(ephemeral=True)

        # I dont think we need this, but imma keep it for now.
        # If its useless, imma push a commit where its removed.
        # -----------------------------------------------------
        # allowed = await self.bot.reminder_db.get("allowed")
        # if not any(x.id in allowed for x in inter.author.roles[1:]):
        #     await inter.send("You're not allowed to use this command.")

        self.remind_view = ReminderMessageView(self.bot)
        self.time = 86400 * days + 3600 * hours + 60 * minutes + seconds

        reminder_msg = await inter.channel.send(
            content=ping_role.mention if ping_role else str(),
            embed=disnake.Embed(title=title, description=message).add_field(
                name="Time", value=f"<t:{int(time.time() + self.time)}:F>"
            ),
            view=self.remind_view,
        )
        db_id = str(reminder_msg.id)
        self.remind_view.db_id = db_id
        await self.bot.reminder_db.put(
            dict(
                time=time.time() + self.time,
                creation_time=int(time.time()),
                title=title,
                message=message,
                channel=str(inter.channel.id),
                users=[],
            ),
            key=db_id,
        )
        await inter.send(content="Message sent.")

        await asyncio.sleep(self.time)
        await self.text_users(db_id, self.remind_view.reacted_users)

    async def text_users(self, db_id: str, users: list[str | int]):
        for user in users:
            user = self.bot.get_user(int(user))
            reminder = await self.bot.reminder_db.get(db_id)
            embed = disnake.Embed(
                title=reminder["title"],
                description="Hey, {user.mention}!\n<t:{creation}:R> someone in Zero Inc set a reminder for **{title}**. So I reminded you about it because you asked me to.".format(
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
        await self.bot.reminder_db.delete(db_id)
        await msg.edit(view=None)

    @publicremind.sub_command()
    async def set_backup_channel(
        self, inter: disnake.CommandInteraction, channel: disnake.TextChannel
    ):
        """
        If the user has DMs turned off, the user will be reminded in this channel.
        """

        await self.bot.reminder_db.put(str(channel.id), key="channel")
        await inter.send(f"Backup channel has been set to {channel.mention}")
