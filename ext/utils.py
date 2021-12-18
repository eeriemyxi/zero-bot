import disnake
from disnake.ext import commands

def parse_desc(text: str, limit: int):
    if len(text) > limit:
        return text[:limit] + "..."
    else:
        return text

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def getch_channel(bot: commands.Bot, channel_id: int) -> disnake.abc.GuildChannel:
    channel = bot.get_channel(channel_id)

    if channel is None:
        channel = await bot.fetch_channel(channel_id)
    return channel


async def getch_role(guild: disnake.Guild, role_id: int) -> disnake.abc.GuildChannel:
    role = guild.get_role(role_id)

    if role is None:
        role = await guild.fetch_role(role_id)
    return role