from contextlib import suppress

import disnake
from ddg_scraper import DuckScraper
from disnake.ext import commands
from ext.paginator import Paginator


duck_scraper = DuckScraper()

class DuckSearch(commands.Cog):
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
        embeds = list()

        with suppress(ValueError):
            async with duck_scraper.search(query) as results:
                async for result in results:
                    embed = disnake.Embed(
                        title=result.title, url=result.url, description=result.snippet
                    )
                    embed.set_thumbnail(result.favicon)
                    embeds.append(embed)

        paginator = Paginator(inter, embeds)
        await inter.edit_original_message(embed=paginator.current_embed, view=paginator)
