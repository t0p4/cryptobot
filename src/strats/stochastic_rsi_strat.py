import pandas as pd
from base_strat import BaseStrategy
from src.utils.logger import Logger

log = Logger(__name__)


class StochasticRSIStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.sma_window = options['sma_window']
        self.rsi_window = options['rsi_window']
        self.minor_tick = options['minor_tick']
        self.major_tick = options['major_tick']
        self.stat_key = options['stat_key']

    def handle_data(self, data, major_tick):
        log.info('Stochastic RSI Strat :: handle_data')
        for mkt_name, mkt_data in data.iteritems():
            if len(mkt_data) >= self.major_tick:
                mkt_data = self.calc_stochastic_rsi(mkt_data)
                tail = mkt_data.tail(2)

                current_tick_buy = (tail['STOCH_RSI'].values[1] >= tail['STOCH_RSI_SMA'].values[1]) and (
                tail['STOCH_RSI'].values[0] < tail['STOCH_RSI_SMA'].values[0])

                current_tick_sell = (tail['STOCH_RSI'].values[1] <= tail['STOCH_RSI_SMA'].values[1]) and (
                    tail['STOCH_RSI'].values[0] > tail['STOCH_RSI_SMA'].values[0])

                if current_tick_buy:
                    log.info(' * * * BUY :: ' + mkt_name)
                    self.buy_positions[mkt_name] = True
                    self.sell_positions[mkt_name] = False
                elif current_tick_sell:
                    log.info(' * * * SELL :: ' + mkt_name)
                    self.buy_positions[mkt_name] = False
                    self.sell_positions[mkt_name] = True
                else:
                    log.debug(' * * * HOLD :: ' + mkt_name)
                    self.buy_positions[mkt_name] = False
                    self.sell_positions[mkt_name] = False
            data[mkt_name] = mkt_data
        return data

    def calc_stochastic_rsi(self, df):
        df['GAIN'] = 0.0
        df['LOSS'] = 0.0
        for idx, data in df.iterrows():
            if idx == 0:
                continue
            change = data[self.stat_key] - df.loc[(idx - 1), self.stat_key]
            if change >= 0:
                df.set_value(idx, 'GAIN', change)
            else:
                df.set_value(idx, 'LOSS', change)
        df['GAIN'] = df['GAIN'].rolling(window=self.rsi_window, center=False).sum()
        df['LOSS'] = df['LOSS'].rolling(window=self.rsi_window, center=False).sum()
        df['RSI'] = 100 - (100 / (1 + df['GAIN'] / df['LOSS']))
        df['MAX_RSI'] = df['RSI'].rolling(window=self.rsi_window, center=False).max()
        df['MIN_RSI'] = df['RSI'].rolling(window=self.rsi_window, center=False).min()
        df['STOCH_RSI'] = df.apply(self.calc_stoch, axis=1)
        df['STOCH_RSI_SMA'] = df['STOCH_RSI'].rolling(window=self.rsi_window, center=False).mean()
        return df

    @staticmethod
    def calc_stoch(data):
        # stoch_rsi = (rsi - lowest_low_rsi) / (highest_high_rsi - lowest_low_rsi)
        return (data['RSI'] - data['MIN_RSI']) / (data['MAX_RSI'] - data['MIN_RSI'])
