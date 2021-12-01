import disnake
from ddg_scraper import asearch
from disnake.ext import commands
from ext.utils import parse_desc, chunks
from ext.paginator import Paginator

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
        # embed = disnake.Embed(title="Web search")
        embeds = list()
        try:
            async for result in results:
                # if count <= 25:
                #     print(parse_desc(result.description, 100))
                embed = disnake.Embed(title=result.title, url=result.url, description=result.description)
                embeds.append(
                    # f"[**{parse_desc(result.title, 80)}**]({result.url})\n{result.description, 100}"
                    embed
                )
                #     count += 1
                # else:
                #     break
        except ValueError:
            pass
        # embed.description = "\n".join(description)
        # print(len(embed.description))
        paginator = Paginator(inter, embeds)
        await inter.edit_original_message(embed=paginator.current_embed, view=paginator)


def setup(bot):
    bot.add_cog(DuckDuckGoSearch(bot))
