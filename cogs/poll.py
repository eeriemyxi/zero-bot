from collections import Counter

import disnake
from disnake.ext import commands


class PollSelect(disnake.ui.Select):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    async def callback(self, inter):
        await inter.response.defer()
        if inter.author not in self.view.voted:
            self.view.voted[inter.author] = inter.values[0]
            self.view.change_vote(inter.values[0], "+")

            await self.view.inter.edit_original_message(
                content=f">>> {self.view.question}",
                view=self.view,
                embed=self.view.get_embed(),
            )
        elif (
            inter.author in self.view.voted
            and self.view.voted[inter.author] != inter.values[0]
        ):
            self.view.change_vote(self.view.voted[inter.author], "-")
            self.view.voted[inter.author] = inter.values[0]
            self.view.change_vote(inter.values[0], "+")

            await self.view.inter.edit_original_message(
                content=f">>> {self.view.question}",
                view=self.view,
                embed=self.view.get_embed(),
            )
        else:
            await inter.followup.send(
                f"{inter.author.mention} You have already voted for that option.",
                ephemeral=True,
            )


class PollView(disnake.ui.View):
    def __init__(self, inter, question, options):
        super().__init__(timeout=None)
        self.inter = inter
        self.voted = dict()
        self.question = question
        self.options_str = options
        self.message: disnake.Message
        self.add_item(
            PollSelect(
                placeholder="Select poll option", options=self.get_options()
            )
        )

    def get_votes(self, label):
        return self.select_option_votes.get(label)

    def change_vote(self, label, operator="+"):
        for option in self.select_option_votes:
            if label == getattr(option, "label", None):
                if operator == "+":
                    self.select_option_votes.update([option])
                elif operator == "-":
                    if self.select_option_votes[option] > 0:
                        self.select_option_votes.subtract([option])
                return

    def get_embed(self):
        embed = disnake.Embed(title="Options")
        for option in self.select_options:
            embed.add_field(
                name=option.label,
                value=f"{option.description}\nVotes: {self.get_votes(option)}",
                inline=False,
            )
        return embed

    def _get_index(self, l, index):
        try:
            return l[index]
        except IndexError:
            return "Not specified"

    def get_options(self):
        options = [option.strip() for option in self.options_str.split("|")]
        self.select_options = list()

        for option in options:
            option = [i.strip() for i in option.split(":")]
            self.select_options.append(
                disnake.SelectOption(
                    label=option[0], description=self._get_index(option, 1)
                )
            )

        self.select_option_votes = Counter(
            {option: 0 for option in self.select_options}
        )
        return self.select_options


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def poll(self, inter, question: str, options: str):
        """
        Make a poll for a question.

        Parameters
        ----------
        question: Your question as text.
        options: List of options. Split them by `|`. You can set desc.. for each option by splitting them with `:`.
        """
        await inter.response.defer()
        poll_view = PollView(inter, question, options)
        poll_view.message = await inter.edit_original_message(
            content=f">>> **{question}**", embed=poll_view.get_embed(), view=poll_view
        )


def setup(bot):
    bot.add_cog(Poll(bot))
