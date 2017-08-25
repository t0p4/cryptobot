from base_strat import BaseStrategy
import pandas as pd


class BollingerBandsStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.num_standard_devs = options['num_standard_devs']
        self.sma_window = options['sma_window']
        self.sma_stat_key = options['sma_stat_key']
        self.minor_tick = options['minor_tick']
        self.major_tick = options['major_tick']

    def handle_data(self, data, tick):
        if tick % self.major_tick == 0:
            for mkt_name, mkt_data in data.iteritems():
                mkt_data.drop(['MarketName', 'TimeStamp', 'PrevDay', 'Created', 'DisplayMarketName'], axis=1, inplace=True)
                mkt_data = mkt_data.groupby(mkt_data.index / 10).mean()
                mkt_data = self.calc_bollinger_bands(mkt_data)
                tail = mkt_data.tail
                if tail['Last'] >= tail['UPPER_BB']:
                    self.buy_positions[mkt_name] = True
                    self.sell_positions[mkt_name] = False
                elif tail['Last'] < tail['UPPER_BB']:
                    self.buy_positions[mkt_name] = False
                    self.sell_positions[mkt_name] = True

    def calc_bollinger_bands(self, df):
        df['SMA'] = pd.rolling_mean(df[self.sma_stat_key], self.sma_window)
        df['STDDEV'] = pd.rolling_std(df[self.sma_stat_key], self.sma_window)
        df['UPPER_BB'] = df['SMA'] + self.num_standard_devs * df['STDDEV']
        df['LOWER_BB'] = df['SMA'] - self.num_standard_devs * df['STDDEV']
        return df
