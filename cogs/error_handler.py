import disnake
import traceback
from disnake.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        match error:
            case commands.CommandNotFound() | commands.MissingRequiredArgument():
                return
            case _:
                await ctx.send(
                    "An uncaught exception has occurred. The developer who is responsible for the error has been cautioned."
                )

                tb = "".join(traceback.format_exception(error))

                user = self.bot.get_user(self.bot.owner_id)
                try:
                    await user.send(f"```py\n{tb}\n```")
                except Exception:
                    raise error
