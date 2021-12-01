from os import getenv

from dotenv import load_dotenv
from pkgutil import iter_modules
from disnake.ext import commands

load_dotenv()


class ZeroBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print("Zero Bot is ready.")


bot = ZeroBot(command_prefix=".", test_guilds=[849636268832325642])
bot.load_extension("jishaku")

for cog in iter_modules(["cogs"]):
    bot.load_extension(f"cogs.{cog.name}")
    print(f"Loaded cog: {cog.name}")

bot.run(token=getenv("TOKEN"))
