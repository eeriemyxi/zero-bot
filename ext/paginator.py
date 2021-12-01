import random
from collections import namedtuple
from contextlib import suppress

import disnake


class Paginator(disnake.ui.View):
    """
    This is my paginator. Currently used to paginate the image search results and my help command.
    Parameters
    ----------
    ctx: :class:`disnake.ext.commands.Context`
        `commands.Context` object of the command
    embeds: :class:`list`
        A list of `disnake.Embed` for pagination
    """

    def __init__(self, inter, embeds: list):
        super().__init__(timeout=80.0)
        self.inter = inter
        self.embeds = embeds
        self.pages = len(self.embeds)
        self.current_page = 0
        self.btn_id = namedtuple(
            "ID", ("NEXT", "BACK", "CANCEL", "RANDOM", "DELETE", "JUMP")
        )("N", "B", "C", "R", "D", "J")
        self.btn_items = namedtuple(
            "ITEMS", ("NEXT", "BACK", "CANCEL", "RANDOM", "DELETE", "JUMP")
        )(
            self.next_button,
            self.back_button,
            self.cancel_button,
            self.random_button,
            self.delete_button,
            self.jump_button,
        )
        self.confirmation = None

    @property
    def current_embed(self) -> disnake.Embed:
        return self.embeds[self.current_page].set_footer(
            text="Page {} of {}".format(self.current_page + 1, self.pages)
        )

    def remove_button(self, button_id: str) -> None:
        if button_id in self.btn_items._asdict():
            self.remove_item(self.btn_items._asdict()[button_id])

    def current_page_set(self, cmd: str = "next", value: int = None):
        """
        Sets the current page.
        Parameters
        ----------
        cmd: :class:`str`
            "random": It will pick a number between 0 and :variable:`self.pages`.
            "next": It will increase the current page number by one.
            "back": It will decrese the current page number by one.
        value: :class:`int`
            If not None, It will set :variable:`self.current_page` to :variable:`value`.
        """

        if value is not None:
            self.current_page = value
            return
        assert cmd in (
            "next",
            "random",
            "back",
        ), "Parameter `cmd` must be any of these: ['next', 'random', 'back']"
        if cmd == "next":
            self.current_page = (
                self.current_page + 1
                if self.current_page < (self.pages - 1)
                else (self.pages - 1)
            )
            return
        if cmd == "random":
            self.current_page = random.randint(0, self.pages - 1)
            return
        self.current_page -= 1 if self.current_page > 0 else 0
        return

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        return interaction.author.id == self.inter.author.id

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.inter.edit_original_message(embed=self.current_embed, view=self)

    @disnake.ui.button(label="Back", emoji="◀️", style=disnake.ButtonStyle.green)
    async def back_button(self, button, inter):
        await inter.response.defer()
        self.value = self.btn_id.BACK
        self.current_page_set("back")
        await self.inter.edit_original_message(embed=self.current_embed)

    @disnake.ui.button(label="Random", emoji="🔢", style=disnake.ButtonStyle.blurple)
    async def random_button(self, button, inter):
        await inter.response.defer()
        self.value = self.btn_id.RANDOM
        self.current_page_set("random")
        await self.inter.edit_original_message(embed=self.current_embed)

    @disnake.ui.button(
        label="Jump", emoji="#️⃣", style=disnake.ButtonStyle.blurple, row=0
    )
    async def jump_button(self, button, inter):
        self.value = self.btn_id.JUMP
        await inter.response.defer()
        ask = await inter.followup.send(
            embed=disnake.Embed(
                title="Select page",
                description=f"Enter a page number between (1 - {self.pages}):",
            )
        )
        msg = await self.inter.bot.wait_for(
            "message",
            check=lambda m: m.author == self.inter.author
            and m.channel == self.inter.channel,
            timeout=80.0,
        )
        if msg.content.isnumeric():
            msg_int = int(msg.content)
            if msg_int > 0 and msg_int <= (self.pages):
                self.current_page_set(value=msg_int - 1)
        await self.inter.edit_original_message(embed=self.current_embed)
        await ask.delete()
        with suppress(Exception):
            await msg.delete()

    @disnake.ui.button(label="Next", emoji="▶️", style=disnake.ButtonStyle.green, row=0)
    async def next_button(self, button, inter):
        await inter.response.defer()
        self.value = self.btn_id.NEXT
        self.current_page_set("next")
        await self.inter.edit_original_message(embed=self.current_embed)

    @disnake.ui.button(label="Cancel", emoji="❌", style=disnake.ButtonStyle.red, row=1)
    async def cancel_button(self, button, inter):
        await inter.response.defer()
        self.value = self.btn_id.CANCEL
        for item in self.children:
            item.disabled = True
        await self.inter.edit_original_message(embed=self.current_embed, view=self)
        self.stop()

    @disnake.ui.button(label="Delete", emoji="🗑️", style=disnake.ButtonStyle.red, row=1)
    async def delete_button(self, button, inter):
        await inter.response.defer()
        self.value = self.btn_id.DELETE
        await self.inter.delete_original_message()
        self.stop()
