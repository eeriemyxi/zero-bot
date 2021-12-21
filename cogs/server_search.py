import disnake
import httpx
from disnake.ext import commands
from ext.paginator import Paginator
from ext.utils import parse_desc
from selectolax.parser import HTMLParser
from yarl import URL


class Search:
    def __init__(self, inter, keywords: str, page: int = 1, limit: int = 0):
        self.inter = inter
        self.keywords = keywords
        self.page = str(page)
        self.limit = limit
        self.disboard = URL("https://disboard.org")
        self.search_baseurl = URL("https://disboard.org/search")
        self.server_baseurl = URL("https://disboard.org/servers/tag")

    @property
    def url(self):
        if " " in self.keywords:
            return self.search_baseurl.with_query(keyword=self.keywords, page=self.page)
        else:
            return self.server_baseurl / self.keywords / self.page

    async def get_html(self):
        async with httpx.AsyncClient() as client:
            content = await client.get(self.url.human_repr())
            return content.text

    async def get_results(self):
        html = await self.get_html()
        parser = HTMLParser(html, True)
        cards = parser.css(".listing-card")
        yields = 0
        if not len(cards):
            await self.inter.followup.send(
                embed=disnake.Embed(title="No results found."), ephemeral=True
            )
            return
        for card in cards:
            tags = [i.text(strip=True) for i in card.css(".tag")]
            name = card.css_first(".server-name").text(strip=True)
            online = card.css_first(".server-online").text(strip=True)
            description = parse_desc(card.css_first(".server-description").text(), 1000)
            icon = next(next(card.css_first(".server-icon").iter()).iter()).attrs["src"]
            server_link = (
                self.disboard
                / next(card.css_first(".server-name").iter()).attrs["href"][1:]
            )
            join_link = (
                self.disboard
                / next(card.css_first(".server-join").iter()).attrs["href"][1:]
            )
            if self.limit == 0 or yields < self.limit:
                yield (
                    dict(
                        tags=tags,
                        icon=icon,
                        name=name,
                        online=online,
                        description=description,
                        links=(join_link, server_link),
                    )
                )
                yields += 1
            else:
                return

    async def get_embeds(self):
        results = self.get_results()
        embeds: list[disnake.Embed] = list()
        async for result in results:
            embed = disnake.Embed()
            embed.title = result.get("name")
            embed.description = result.get("description")
            join, server = result.get("links")
            embed.add_field(name="Online member count", value=result.get("online"))
            embed.add_field(name="Tags", value=", ".join(result.get("tags")))
            embed.add_field(
                name="Links",
                value=f"[Server profile]({server})\n[Join]({join})",
                inline=False,
            )
            if "http" in (icon := result.get("icon")):
                embed.set_thumbnail(icon)
            embeds.append(embed)
        return embeds


class ServerSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def serversearch(self, inter, keywords: str, page: int = 1, limit: int = 0):
        """
        Searches for servers on `disbaord.org`.

        Parameters
        ----------
        keywords: Tags to search. Split them by a whitespace.
        page: Page number to show servers of. Defaults to 1.
        limit: Maximum number of results to return. Defaults to 0, meaning no limit.
        """
        await inter.response.defer()
        try:
            embeds = await Search(inter, keywords, page, limit).get_embeds()
        except AttributeError:
            await inter.followup.send(embed=disnake.Embed(title="**Not found.**"))
            return
        paginator = Paginator(inter, embeds)
        await inter.followup.send(embed=paginator.current_embed, view=paginator)


# def setup(bot):
#     bot.add_cog(ServerSearch(bot))
