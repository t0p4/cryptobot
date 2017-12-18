import pandas as pd
from base_strat import BaseStrategy
from src.utils.logger import Logger

log = Logger(__name__)


class VolumeStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.major_tick = options['major_tick']
        self.pvo_ema_period = options['pvo_ema_period']
        self.short_vol_ema_period = options['short_vol_ema_period']
        self.long_vol_ema_period = options['long_vol_ema_period']
        self.vol_roc_period = options['vol_roc_period']
        self.is_active = False

    def handle_data(self, data, major_tick):
        log.info('Stochastic RSI Strat :: handle_data')
        for mkt_name, mkt_data in data.iteritems():
            if len(mkt_data) > self.long_vol_ema_period:
                mkt_data = self.calc_volume_metrics(mkt_data)
                if len(mkt_data) > self.long_vol_ema_period + self.pvo_ema_period:
                    buy = False
                    sell = False
                    tail = mkt_data.tail(3).reset_index(drop=True)

                    pvo_up = tail.loc[2, 'PVO'] > tail.loc[2, 'PVO_EMA']
                    pvo_down_1 = tail.loc[1, 'PVO'] < tail.loc[1, 'PVO_EMA']
                    pvo_down_2 = tail.loc[0, 'PVO'] < tail.loc[0, 'PVO_EMA']

                    if pvo_up and (pvo_down_1 or pvo_down_2):
                        buy = True
                    if not pvo_up and (not pvo_down_1 or not pvo_down_2):
                        sell = True
                    if buy:
                        log.info(' * * * BUY :: ' + mkt_name)
                        self.buy_positions[mkt_name] = True
                        self.sell_positions[mkt_name] = False
                    elif sell:
                        log.info(' * * * SELL :: ' + mkt_name)
                        self.buy_positions[mkt_name] = False
                        self.sell_positions[mkt_name] = True
                    else:
                        log.debug(' * * * HOLD :: ' + mkt_name)
                        self.buy_positions[mkt_name] = False
                        self.sell_positions[mkt_name] = False
            else:
                mkt_data['SHORT_VOL_EMA'] = mkt_data['volume'].rolling(window=self.short_vol_ema_period,
                                                                            center=False).mean()
                mkt_data['LONG_VOL_EMA'] = mkt_data['volume'].rolling(window=self.long_vol_ema_period,
                                                                            center=False).mean()
            data[mkt_name] = mkt_data
        return data

    def calc_volume_metrics(self, df):
        # calculate stats
        df = self.calc_volume_osc(df)
        # df = self.calc_volume_roc(df)

        return df

    def calc_volume_roc(self, df):
        # VOL_ROC = ( ( current_vol / vol_n_periods_back ) - 1 ) / 100
        return df

    def calc_volume_osc(self, df):
        # PVO = ( ( short_vol_ema - long_vol_ema ) / long_vol_ema ) * 100

        # cutoff tail, sized by window
        tail = df.tail(2).reset_index(drop=True)

        # drop last row, will be replaced after calculation
        df = df.drop(df.index[-1:])

        # calculate short EMA
        tail = self.set_ema(tail, 'SHORT_VOL_EMA', self.short_vol_ema_period, 'volume')

        # calculate long EMA
        tail = self.set_ema(tail, 'LONG_VOL_EMA', self.long_vol_ema_period, 'volume')

        # calculate PVO
        pvo = ((tail.loc[1, 'SHORT_VOL_EMA'] - tail.loc[1, 'LONG_VOL_EMA']) / tail.loc[1, 'LONG_VOL_EMA']) * 100
        tail.set_value(1, 'PVO', pvo)

        # if we have calculated enough PVO's, start calculating the PVO_EMA
        # else calculate PVO_SMA
        if len(df) >= self.long_vol_ema_period + self.pvo_ema_period:
            self.is_active = True
            # calculate PVO EMA
            tail = self.set_ema(tail, 'PVO_EMA', self.pvo_ema_period, 'PVO')
            return df.append(tail.tail(1), ignore_index=True)
        else:
            df = df.append(tail.tail(1), ignore_index=True)
            df['PVO_EMA'] = df['PVO'].rolling(window=self.pvo_ema_period, center=False).mean()
            return df

    def set_ema(self, df, ema_key, ema_period, stat_key):
        prev_ema = df.loc[0, ema_key]
        next_ema = self.calc_ema(df, ema_period, prev_ema, stat_key)
        df.set_value(1, ema_key, next_ema)
        return df

    @staticmethod
    def calc_ema(df, period, prev_ema, stat_key):
        # EMA = (last - prev_ema) * multiplier + prev_ema
        multiplier = 2.0 / (period + 1)
        return (df.loc[1, stat_key] - prev_ema) * multiplier + prev_ema
