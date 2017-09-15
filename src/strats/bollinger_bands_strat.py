import pandas as pd
from base_strat import BaseStrategy
from src.utils.logger import Logger
log = Logger(__name__)


class BollingerBandsStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.num_standard_devs = options['num_standard_devs']
        self.sma_window = options['sma_window']
        self.sma_stat_key = options['sma_stat_key']
        self.minor_tick = options['minor_tick']
        self.major_tick = options['major_tick']

    def handle_data(self, data, major_tick):
        log.info('Bollinger Band Strat :: handle_data')
        for mkt_name, mkt_data in data.iteritems():
            mkt_data = self.compress_and_calculate_mean(mkt_data)
            if len(mkt_data) >= self.major_tick:
                mkt_data = self.calc_bollinger_bands(mkt_data)
                tail = mkt_data.tail(2)
                current_tick_buy = tail['last'].values[1] >= tail['UPPER_BB'].values[1]
                current_tick_sell = tail['last'].values[0] < tail['UPPER_BB'].values[0]
                prev_tick_buy = tail['last'].values[1] >= tail['UPPER_BB'].values[1]
                prev_tick_sell = tail['last'].values[0] < tail['UPPER_BB'].values[0]
                if current_tick_buy and prev_tick_sell:
                    log.info(' * * * BUY :: ' + mkt_name)
                    self.buy_positions[mkt_name] = True
                    self.sell_positions[mkt_name] = False
                elif current_tick_sell and prev_tick_buy:
                    log.info(' * * * SELL :: ' + mkt_name)
                    self.buy_positions[mkt_name] = False
                    self.sell_positions[mkt_name] = True
                else:
                    log.debug(' * * * HOLD :: ' + mkt_name)
                    self.buy_positions[mkt_name] = False
                    self.sell_positions[mkt_name] = False
            data[mkt_name] = mkt_data
        return data

    def compress_and_calculate_mean(self, data):
        data = data[['last', 'bid', 'ask', 'saved_timestamp', 'marketname']]
        # data = data[['volume', 'last', 'bid', 'ask', 'basevolume', 'openbuyorders', 'opensellorders', 'saved_timestamp', 'ticker_nonce']]
        tail = data.tail(self.major_tick).reset_index(drop=True)
        tail_meta_data = tail[['marketname', 'saved_timestamp']].tail(1).reset_index(drop=True)
        data = data.drop(data.index[-self.major_tick:])
        tail = pd.concat([tail.groupby(tail.index / self.major_tick).mean(), tail_meta_data], axis=1, join_axes=[tail_meta_data.index])
        return data.append(tail, ignore_index=True)

    def calc_bollinger_bands(self, df):
        df['SMA'] = df[self.sma_stat_key].rolling(window=self.sma_window, center=False).mean()
        df['STDDEV'] = df[self.sma_stat_key].rolling(window=self.sma_window, center=False).std()
        df['UPPER_BB'] = df['SMA'] + self.num_standard_devs * df['STDDEV']
        df['LOWER_BB'] = df['SMA'] - self.num_standard_devs * df['STDDEV']
        return df
