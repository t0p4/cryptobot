import pandas as pd
from base_strat import BaseStrategy
from src.utils.logger import Logger
from datetime import datetime

log = Logger(__name__)


class StochasticRSIStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.sma_window = options['sma_window']
        self.rsi_window = options['rsi_window']
        self.minor_tick = options['minor_tick']
        self.major_tick = options['major_tick']
        self.stat_key = options['stat_key']
        self.columns_initialized = False

    def handle_data(self, data, major_tick):
        log.info('Stochastic RSI Strat :: handle_data')
        start = datetime.now()
        for mkt_name, mkt_data in data.iteritems():
            mkt_data = self.calc_stochastic_rsi(mkt_data)
            tail = mkt_data.tail(2)
            if len(mkt_data.index) >= self.rsi_window + 1:
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
        end = datetime.now()
        log.info('runtime :: ' + str(end - start))
        return data

    def calc_stochastic_rsi(self, df):
        if len(df.index) == 1:
            df = self.init_columns(df)
            return df

        # optimize calculations by getting tail
        tail = df.tail(self.rsi_window)
        df = df.drop(df.index[-self.rsi_window:])
        tail_len = len(tail.index)

        # calculate change
        change = tail.loc[(tail_len - 1), self.stat_key] - tail.loc[(tail_len - 2), self.stat_key]
        if change >= 0:
            df.set_value(tail_len - 1, 'GAIN', change)
        else:
            df.set_value(tail_len - 1, 'LOSS', change)

        # don't start calculating rsi and stochastic rsi until the window is filled
        if len(tail.index) == self.rsi_window:
            if len(df.index) == self.rsi_window:
                total_gains = tail['GAIN'].rolling(window=self.rsi_window, center=False).sum()
                total_losses = tail['LOSS'].rolling(window=self.rsi_window, center=False).sum()
                avg_gain = total_gains / self.rsi_window
                avg_loss = total_losses / self.rsi_window
                tail.set_value(self.rsi_window - 1, 'AVG_GAIN', avg_gain)
                tail.set_value(self.rsi_window - 1, 'AVG_LOSS', avg_loss)
                rs = avg_gain / avg_loss
            else:
                prev_avg_gain = tail.loc[self.rsi_window - 2, 'AVG_GAIN']
                prev_avg_loss = tail.loc[self.rsi_window - 2, 'AVG_LOSS']
                num = ((prev_avg_gain * (self.rsi_window - 1)) + tail.loc[self.rsi_window - 1, 'GAIN']) / self.rsi_window
                den = ((prev_avg_loss * (self.rsi_window - 1)) + tail.loc[self.rsi_window - 1, 'LOSS']) / self.rsi_window
                rs = num / den
            tail.set_value(self.rsi_window - 1, 'RSI', 100 - (100 / (1 + rs)))

            max_rsi = tail['RSI'].rolling(window=self.rsi_window, center=False).max()
            min_rsi = tail['RSI'].rolling(window=self.rsi_window, center=False).min()
            rsi = tail.loc[self.rsi_window - 1, 'RSI']
            stochastic_rsi = (rsi - min_rsi) / (max_rsi - min_rsi)
            tail.set_value(self.rsi_window - 1, 'STOCH_RSI', stochastic_rsi)
            stochastic_rsi_sma = tail['STOCH_RSI'].rolling(window=self.sma_window, center=False).mean()
            tail.set_value(self.rsi_window - 1, 'STOCH_RSI_SMA', stochastic_rsi_sma)
        return df.append(tail, ignore_index=True)

    def init_columns(self, df):
        if not self.columns_initialized:
            df['GAIN'] = 0.0
            df['LOSS'] = 0.0
            df['AVG_GAIN'] = 0.0
            df['AVG_LOSS'] = 0.0
            df['RSI'] = 0.0
            df['MAX_RSI'] = 0.0
            df['MIN_RSI'] = 0.0
            df['STOCH_RSI'] = 0.0
            df['STOCH_RSI_SMA'] = 0.0
            self.columns_initialized = True
        return df
