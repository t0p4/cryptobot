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
                mkt_data = self.compress_and_calculate_mean(mkt_data)
                mkt_data = self.calc_bollinger_bands(mkt_data)
                tail = mkt_data.tail()
                if tail['last'].values[0] >= tail['UPPER_BB'].values[0]:
                    self.buy_positions[mkt_name] = True
                    self.sell_positions[mkt_name] = False
                elif tail['last'].values[0] < tail['UPPER_BB'].values[0]:
                    self.buy_positions[mkt_name] = False
                    self.sell_positions[mkt_name] = True

    def compress_and_calculate_mean(self, data):
        data = data[['volume', 'last', 'bid', 'ask', 'basevolume', 'openbuyorders', 'opensellorders']]
        # data = data[['volume', 'last', 'bid', 'ask', 'basevolume', 'openbuyorders', 'opensellorders', 'saved_timestamp', 'ticker_nonce']]
        tail = data.tail(self.major_tick).reset_index(drop=True)
        data = data.drop(data.index[-self.major_tick:])
        tail = tail.groupby(tail.index / self.major_tick).mean()
        return data.append(tail, ignore_index=True)

    def calc_bollinger_bands(self, df):
        df['SMA'] = pd.rolling_mean(df[self.sma_stat_key], self.sma_window)
        df['STDDEV'] = pd.rolling_std(df[self.sma_stat_key], self.sma_window)
        df['UPPER_BB'] = df['SMA'] + self.num_standard_devs * df['STDDEV']
        df['LOWER_BB'] = df['SMA'] - self.num_standard_devs * df['STDDEV']
        return df