from importlib import import_module
from os import system
from pkgutil import iter_modules, ModuleInfo

try:
    from disnake.ext import commands  # type: ignore
except ImportError:
    from discord.ext import commands  # type: ignore


def snake_to_pascal(string):
    init, *temp = string.split("_")
    return "".join([init.capitalize(), *map(str.title, temp)])


class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    END = "\033[0m"


class Package:
    def __init__(self, folder_name: str, module: ModuleInfo):
        self.module = module
        self.name = module.name
        self.full = f"{folder_name}.{self.name}"


class Loader:
    def __init__(self, bot: commands.Bot, folder_name: str = None):
        self.bot = bot
        self.folder_name = folder_name
        system("")

    @property
    def packages(self):
        for pkg in sorted(iter_modules([self.folder_name]), key=lambda x: x.name):
            yield Package(self.folder_name, pkg)

    def load_cogs(self):
        for pkg in self.packages:
            module = import_module(pkg.full)
            cog_name = snake_to_pascal(pkg.name)
            cog = getattr(module, cog_name, None)

            if cog is not None:
                self.bot.add_cog(cog(self.bot))
                print(f"{Color.GREEN}Loaded COG: {Color.RED}{cog_name}{Color.END}")
            else:
                continue
