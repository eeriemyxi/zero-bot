from os import getenv
from ast import literal_eval

from aiohttp import ClientSession
from deta import Deta
from disnake import Embed, Intents, Webhook
from disnake.ext import commands
from dotenv import load_dotenv

from loader import Loader

load_dotenv()


class ZeroBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deta = Deta(getenv("KEY"))
        self.db = self.deta.AsyncBase("db")
        self.reminder_db = self.deta.AsyncBase("reminder_db")
        self.pers_views = False
        self.already_started = False

    async def on_ready(self):
        self.session = ClientSession()
        print(f"{self.user.name} is ready.")
        if not self.already_started:
            self.webhook = Webhook.from_url(
                getenv("BOT_LOG_WEBHOOK"), session=self.session
            )
            await self.webhook.send(
                embed=Embed(title=self.user.name, description="Bot started.")
            )
            self.already_started = True


bot = ZeroBot(
    command_prefix=".",
    test_guilds=literal_eval(getenv("TEST_GUILDS")),
    intents=Intents.all(),
)
bot.load_extension("jishaku")
loader = Loader(bot, "cogs")
COG_BLACKLIST = []


loader.load_cogs()
bot.run(token=getenv("TOKEN"))
