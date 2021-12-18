from os import getenv

from dotenv import load_dotenv
from pkgutil import iter_modules
from disnake import Intents, Webhook, Embed
from disnake.ext import commands
from deta import Deta
from aiohttp import ClientSession

load_dotenv()


class ZeroBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deta = Deta(getenv("KEY"))
        self.db = self.deta.AsyncBase("db")
        self.pers_views = False
        self.already_started = False

    async def on_ready(self):
        print(f"{self.user.name} is ready.")
        if not self.already_started:
            async with ClientSession() as session:
                self.webhook = Webhook.from_url(getenv("BOT_LOG_WEBHOOK"), session=session)
                await self.webhook.send(embed=Embed(title=self.user.name, description="Bot started."))
                self.already_started = True


bot = ZeroBot(command_prefix=".", test_guilds=[849636268832325642, 858720379069136896], intents=Intents.all())
bot.load_extension("jishaku")
COG_BLACKLIST = []

for cog in iter_modules(["cogs"]):
    if cog.name not in COG_BLACKLIST:
        bot.load_extension(f"cogs.{cog.name}")
        print(f"Loaded cog: {cog.name}")

bot.run(token=getenv("TOKEN"))
