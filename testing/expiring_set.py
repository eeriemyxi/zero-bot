from dataclasses import dataclass
import threading
import time


@dataclass
class ActiveLogMessage:
    time: int
    author: int

    def __hash__(self):
        return hash(self.author)


class ExpiringSet:
    def __init__(self, expiry_time: int):
        self.data: set[ActiveLogMessage] = set()
        self.expiry_time = expiry_time

    def add_user(self, msg):
        if not isinstance(msg, ActiveLogMessage):
            log_msg = ActiveLogMessage(msg.created_at.timestamp(), msg.author.id)
        else:
            log_msg = msg

        self.data.add(log_msg)

        thread = threading.Thread(None, target=self.expire, args=[log_msg], daemon=True)
        thread.start()
    
    def get_log_msg(self, author: int) -> ActiveLogMessage:
        for log_msg in self.data.copy():
            if log_msg.author == author:
                return log_msg

    def expire(self, log_msg: ActiveLogMessage):
        time.sleep(self.expiry_time)

        for x in self.data.copy(): 
            if (x.author, x.time) == (log_msg.author, log_msg.time):
                self.data.remove(x)
    
    def __repr__(self) -> str:
        return repr(self.data)


ex_set = ExpiringSet(2)
ex_set.add_user(ActiveLogMessage(time=23, author=1))
ex_set.add_user(ActiveLogMessage(time=23, author=1))
ex_set.add_user(ActiveLogMessage(time=23, author=2))
print(ex_set)
time.sleep(3)
print(ex_set)