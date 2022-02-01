# import time
# from datetime import datetime


# one = datetime.now()
# time.sleep(5)
# two = datetime.now()

# print((two - one).total_seconds())

# import time


# t = 30

# if t > 20:
#     time.sleep(t - 20)
#     t = 20
#     print("works maybe")
# if t > 10:
#     time.sleep(t - 10)
#     t = 10
#     print("idek at this point")

# # print(t)
# print("last 10 seconds")

import asyncio

async def main():
    async def hi(): return 10

    print(await asyncio.gather(*[hi() for _ in range(10)]))

asyncio.run(main())