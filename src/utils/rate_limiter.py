from datetime import datetime, timedelta
from time import sleep
from src.utils.logger import Logger

log = Logger(__name__)


class RateLimiter:
    def __init__(self, name, rate_limit=timedelta(0, 4, 0)):
        self.name = name
        self.rate_limit = rate_limit
        self.tick = None
        self.reset()

    def reset(self):
        self.tick = datetime.now()

    def check(self):
        current_tick = datetime.now()
        return (current_tick - self.tick) < self.rate_limit

    def limit(self):
        current_tick = datetime.now()
        if self.check():
            sleep_for = self.rate_limit - (current_tick - self.tick)
            log.warning('Rate Limit ' + self.name + ' :: sleeping for ' + str(sleep_for) + ' seconds')
            sleep(sleep_for.seconds)
        self.reset()
