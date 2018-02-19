import pandas as pd
from src.strats.base_strat import BaseStrategy
from src.utils.logger import Logger
log = Logger(__name__)


class WilliamsPctStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.wp_window = options['wp_window']
        self.stat_key = options['stat_key']

    def handle_data(self, mkt_data, mkt_name):
        if len(mkt_data) >= self.wp_window:
            mkt_data = self.calculate_williams_pct(mkt_data)
            tail = mkt_data.tail(1)

            buy = tail['W_PCT'].values[0] >= -20
            sell = tail['W_PCT'].values[0] <= -80

            self._set_positions(buy, sell, mkt_name)
        return mkt_data

    def calculate_williams_pct(self, data):
        # get tail, drop last row of data
        window = data.tail(self.wp_window).reset_index(drop=True)
        data = data.drop(data.index[-1:])

        # calculate williams %
        highest = window[self.stat_key].max(axis=0)
        lowest = window[self.stat_key].min(axis=0)
        last = window[self.stat_key].iloc[-1]
        w_pct = (highest - last) / (highest - lowest) * -100
        window.set_value(self.wp_window - 1, 'W_PCT', w_pct)

        return data.append(window.tail(1), ignore_index=True)
