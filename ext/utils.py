from datetime import datetime, timezone

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


def parse_env_data(text: str):
    result = {}
    items = text.split(",")

    for item in items:
        item = [i.strip() for i in item.split(":")]
        result[item[0]] = item[1]

    return result


async def send_message(session, channel_id: int | str, token: str, message: str):
    await session.post(
        url="https://canary.discord.com/api/v9/channels/%s/messages" % channel_id,
        headers=dict(authorization=token),
        json={"content": message, "content-type": "application/json"},
    )

def get_timestamp(day: int, month: int, year: int, time: str) -> int:
    hour, minute, second = time.split(":", 3)

    if "+" in hour:
        hour = int(hour[:-1]) + 12
    else:
        hour = int(hour)

    minute, second = int(minute), int(second)
    dt = datetime(day=day, month=month, year=year, hour=hour, minute=minute, second=second)

    return dt.timestamp()
