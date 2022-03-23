from datetime import datetime


def get_timestamp(day: int, month: int, year: int, time: str) -> int:
    hour, minute, second = time.split(":", 3)

    if "+" in hour:
        hour = int(hour[:-1]) + 12
    else:
        hour = int(hour)

    minute, second = int(minute), int(second)
    dt = datetime(day=day, month=month, year=year, hour=hour, minute=minute, second=second)

    return dt.timestamp()