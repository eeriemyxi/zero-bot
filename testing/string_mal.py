# from datetime import datetime, timezone
import arrow


def get_timestamp(day: int, month: int, year: int, time: str, timezone: str) -> int:
    hour, minute, second = time.split(":", 3)

    if "+" in hour:
        hour = int(hour[:-1]) + 12
    else:
        hour = int(hour)

    minute, second = int(minute), int(second)
    dt = arrow.Arrow(
        day=day,
        month=month,
        year=year,
        hour=hour,
        minute=minute,
        second=second,
        timezone=timezone,
    )

    return dt.int_timestamp


# print(get_timestamp(*map(int, input().split()), "Asia/India")
# )
print(get_timestamp(1, 1, 2021, "7+:20:0", "Asia/India"))
