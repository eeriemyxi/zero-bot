import time
from datetime import datetime


one = datetime.now()
time.sleep(5)
two = datetime.now()

print((two - one).total_seconds())