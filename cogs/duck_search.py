import disnake
from ddg_scraper import asearch
from disnake.ext import commands
from ext.paginator import Paginator

from contextlib import suppress


class DuckDuckGoSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def websearch(self, inter, *, query):
        """
        Shows first 25 search results from DuckDuckGo search engine.

        Parameters
        ----------
        query: Text to search
        """
        await inter.response.defer()
        results = await asearch(query)
        embeds = list()
        with suppress(ValueError):
            async for result in results:
                embed = disnake.Embed(
                    title=result.title, url=result.url, description=result.description
                )
                embeds.append(embed)
        paginator = Paginator(inter, embeds)
        await inter.edit_original_message(embed=paginator.current_embed, view=paginator)


def setup(bot):
    bot.add_cog(DuckDuckGoSearch(bot))
