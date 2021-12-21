from contextlib import suppress

import disnake
from bot import ZeroBot
from disnake.ext import commands


class VerificationSelect(disnake.ui.Select):
    YES = "1"
    NO = "2"

    def __init__(self, db):
        self.db = db
        options = [
            disnake.SelectOption(label="Yes", value=self.YES),
            disnake.SelectOption(label="No", value=self.NO),
        ]
        super().__init__(
            custom_id="verification_view", placeholder="Do you agree?", options=options
        )

    async def callback(self, inter: disnake.MessageInteraction):
        if self.values[0] == self.YES:
            role_id = int((await self.db.get("v_role"))["value"])
            await self.db.put({"members": []}, "verified")
            await self.db.update(
                {"members": self.db.util.append(str(inter.author.id))}, "verified"
            )

            await inter.author.remove_roles(
                inter.guild.get_role(role_id), reason="Verification successful."
            )
            await inter.response.send_message(content="Welcome.", ephemeral=True)
        elif self.values[0] == self.NO:
            await inter.response.send_message("Bye!", ephemeral=True)
            await inter.author.kick()


class VerificationView(disnake.ui.View):
    def __init__(self, db):
        super().__init__(timeout=None)
        self.add_item(VerificationSelect(db))


class Verification(commands.Cog):
    def __init__(self, bot: ZeroBot):
        self.bot = bot
        self.db = self.bot.db

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.pers_views:
            self.bot.add_view(VerificationView(self.db))

            if await self.channel_check():
                channel = self.bot.get_channel(int(self.v_channel_id["value"]))
                message_id = await self.db.get("v_message")
                message = await channel.fetch_message(int(message_id["value"]))
                await message.edit(view=VerificationView(self.db))

            self.bot.pers_views = True
            print("Verification view has been loaded.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = await self.db.get("v_role")
        if role is not None:
            await member.add_roles(member.guild.get_role(int(role["value"])))

    async def channel_check(self):
        self.v_channel_id = await self.db.get("v_channel")
        return self.v_channel_id is not None

    @commands.slash_command()
    async def verification(self, inter):
        pass

    @verification.sub_command(name="set")
    async def set_channel(self, inter, channel: disnake.TextChannel):
        await inter.response.defer()
        await self.db.put(str(channel.id), "v_channel")

        await inter.edit_original_message(
            content=f"Alright, done. I set the verification channel to {channel.mention}. \
                    Use the `update_message` sub command to send or update the message."
        )

    @verification.sub_command()
    async def create_role(self, inter, role_name: str):
        if await self.channel_check() is False:
            return
        else:
            self.v_channel_id = int(self.v_channel_id["value"])

        await inter.response.defer()
        role = await inter.guild.create_role(
            name=role_name, reason="Auto generated for member verification purposes."
        )

        for channel in inter.guild.text_channels + inter.guild.voice_channels:
            if channel.id != self.v_channel_id:
                with suppress(Exception):
                    await channel.set_permissions(
                        role, view_channel=False, send_messages=False
                    )

        await inter.edit_original_message(
            content=f"Done. This role now is only visible to <#{self.v_channel_id}>"
        )
        await self.db.put(str(role.id), "v_role")

    @verification.sub_command()
    async def update_message(self, inter, content: str):
        await inter.response.defer()

        if await self.channel_check() is False:
            return
        else:
            self.v_channel_id = int(self.v_channel_id["value"])

        message_id = await self.db.get("v_message")
        channel = self.bot.get_channel(self.v_channel_id)

        if message_id is not None:
            message = await channel.fetch_message(int(message_id["value"]))
            await message.edit(content=content, view=VerificationView(self.db))
        else:
            msg = await channel.send(content=content, view=VerificationView(self.db))
            await self.db.put(str(msg.id), "v_message")

        await inter.edit_original_message(content="Done.")
