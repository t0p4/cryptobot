import pandas as pd
from base_strat import BaseStrategy
from src.utils.logger import Logger
log = Logger(__name__)


class WilliamsPctStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.wp_window = options['wp_window']
        self.minor_tick = options['minor_tick']
        self.major_tick = options['major_tick']

    def handle_data(self, data, tick):
        print(tick)

    def calculate_williams_pct(self, data):
        window = data.tail(self.wp_window)
        highest = window['last'].max(axis=0)
        lowest = window['last'].min(axis=0)
        last = window['last'].iloc[-1]
        w_pct = (highest - last) / (highest - lowest) * -100
        return w_pct
