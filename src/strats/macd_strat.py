import pandas as pd
from src.strats.base_strat import BaseStrategy
from src.utils.logger import Logger
from datetime import datetime
log = Logger(__name__)


class MACDStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)

        self.sma_window = options['sma_window']
        self.slow_ema_window = options['slow_ema_window']
        self.fast_ema_window = options['fast_ema_window']

    def handle_data(self, mkt_data, mkt_name):
        if len(mkt_data) >= self.slow_ema_window:
            mkt_data = self.calc_macd(mkt_data)
            tail = mkt_data.tail(2)

            # buy = tail['MACD'].values[1] >= tail['MACD_sign'].values[1] and tail['MACD'].values[0] < tail['MACD_sign'].values[0]
            # sell = tail['MACD'].values[1] < tail['MACD_sign'].values[1] and tail['MACD'].values[0] >= tail['MACD_sign'].values[0]

            buy = len(mkt_data) % 20 == 0
            sell = len(mkt_data) % 37 == 0
            self._set_positions(buy, sell, mkt_name)

        return mkt_data

    def calc_macd(self, df):
        # cutoff tail, sized by window

        tail = df.tail(self.slow_ema_window).reset_index(drop=True)
        # drop last row, will be replaced after calculation
        df = df.drop(df.index[-1:])

        # calculate stats
        # tail[['MACD', 'emaSlw', 'emaFst']] = df[self.stat_key].apply(self.moving_average_convergence)
        tail[['MACD', 'emaSlw', 'emaFst']] = self.moving_average_convergence(tail['last'])
        tail['MACD_sign'] = self.moving_average(tail['MACD'])

        # append and return
        return df.append(tail.tail(1), ignore_index=True)

    def moving_average(self, group):
        sma = pd.rolling_mean(group, self.sma_window)
        return sma

    def moving_average_convergence(self, data):
        emaslow = pd.ewma(data, span=self.slow_ema_window, min_periods=1)
        emafast = pd.ewma(data, span=self.fast_ema_window, min_periods=1)
        result = pd.DataFrame({'MACD': emafast - emaslow, 'emaSlw': emaslow, 'emaFst': emafast})
        return result

    def get_mkt_report(self, mkt_name, mkt_data):
        # get standard report data
        report = self._get_mkt_report(mkt_name, mkt_data)

        # calculate:
        # 1) % change over most recent window
        # 2) % change over most recent tick
        tail = mkt_data.tail(self.window).reset_index(drop=True)

        report['strat_specific_data'] = "NO REPORT YET"
        return report
