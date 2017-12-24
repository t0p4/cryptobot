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
        self.stat_key = options['stat_key']

    def handle_data(self, data, tick):
        log.info('Williams % Strat :: handle_data')
        for mkt_name, mkt_data in data.iteritems():
            if len(mkt_data) >= self.major_tick:
                mkt_data = self.calculate_williams_pct(mkt_data)
                tail = mkt_data.tail(1)

                buy = tail['W_PCT'].values[0] >= -20
                sell = tail['W_PCT'].values[0] <= -80

                self.set_positions(buy, sell, mkt_name)
            data[mkt_name] = mkt_data
        return data

    def calculate_williams_pct(self, data):
        window = data.tail(self.wp_window)
        highest = window[self.stat_key].max(axis=0)
        lowest = window[self.stat_key].min(axis=0)
        last = window[self.stat_key].iloc[-1]
        data['W_PCT'] = (highest - last) / (highest - lowest) * -100
        return data
