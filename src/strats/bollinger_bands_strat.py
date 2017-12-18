import pandas as pd
from base_strat import BaseStrategy
from src.utils.logger import Logger
from datetime import datetime
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
        start = datetime.now()
        for mkt_name, mkt_data in data.iteritems():
            if len(mkt_data) >= self.sma_window:
                mkt_data = self.calc_bollinger_bands(mkt_data)
                tail = mkt_data.tail(2)

                # EXTRA
                # current_tick_buy = tail['last'].values[1] >= tail['UPPER_BB'].values[1]
                # current_tick_sell = tail['last'].values[0] < tail['SMA'].values[0]
                # prev_tick_buy = tail['last'].values[1] >= tail['UPPER_BB'].values[1]
                # prev_tick_sell = tail['last'].values[0] < tail['UPPER_BB'].values[0]
                # if current_tick_buy and prev_tick_sell:
                #     log.info(' * * * BUY :: ' + mkt_name)
                #     self.buy_positions[mkt_name] = True
                #     self.sell_positions[mkt_name] = False
                # elif current_tick_sell:
                #     log.info(' * * * SELL :: ' + mkt_name)
                #     self.buy_positions[mkt_name] = False
                #     self.sell_positions[mkt_name] = True
                # else:
                #     log.debug(' * * * HOLD :: ' + mkt_name)
                #     self.buy_positions[mkt_name] = False
                #     self.sell_positions[mkt_name] = False

                # # STANDARD
                buy_it = tail['last'].values[1] < tail['LOWER_BB'].values[1]
                sell_it = tail['last'].values[1] > tail['UPPER_BB'].values[1]
                self.buy_positions[mkt_name] = buy_it
                self.sell_positions[mkt_name] = sell_it

            data[mkt_name] = mkt_data
        end = datetime.now()
        log.info('runtime :: ' + str(end - start))
        return data

    def calc_bollinger_bands(self, df):
        # cutoff tail, sized by window

        tail = df.tail(self.sma_window).reset_index(drop=True)
        # drop last row, will be replaced after calculation
        df = df.drop(df.index[-1:])

        # calculate stats
        tail['SMA'] = tail[self.sma_stat_key].rolling(window=self.sma_window, center=False).mean()
        tail['STDDEV'] = tail[self.sma_stat_key].rolling(window=self.sma_window, center=False).std()
        tail['UPPER_BB'] = tail['SMA'] + self.num_standard_devs * tail['STDDEV']
        tail['LOWER_BB'] = tail['SMA'] - self.num_standard_devs * tail['STDDEV']

        # append and return
        return df.append(tail.tail(1), ignore_index=True)
