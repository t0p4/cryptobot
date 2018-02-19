import pandas as pd
from src.strats.base_strat import BaseStrategy
from src.utils.logger import Logger

log = Logger(__name__)


class VolumeStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.pvo_ema_window = options['pvo_ema_window']
        self.short_vol_ema_window = options['short_vol_ema_window']
        self.long_vol_ema_window = options['long_vol_ema_window']
        self.vol_roc_window = options['vol_roc_window']
        self.is_active = False

    def handle_data(self, mkt_data, mkt_name):
        if len(mkt_data) > self.long_vol_ema_window:
            mkt_data = self.calc_volume_metrics(mkt_data)
            if len(mkt_data) > self.long_vol_ema_window + self.pvo_ema_window:
                tail = mkt_data.tail(2).reset_index(drop=True)

                pvo_up = tail.loc[1, 'PVO'] > tail.loc[1, 'PVO_EMA']
                pvo_down_1 = tail.loc[0, 'PVO'] < tail.loc[0, 'PVO_EMA']

                buy = pvo_up and pvo_down_1
                sell = not pvo_up and not pvo_down_1

                self._set_positions(buy, sell, mkt_name)
        else:
            mkt_data['SHORT_VOL_EMA'] = mkt_data[self.stat_key].rolling(window=self.short_vol_ema_window,
                                                                        center=False).mean()
            mkt_data['LONG_VOL_EMA'] = mkt_data[self.stat_key].rolling(window=self.long_vol_ema_window,
                                                                        center=False).mean()
        return mkt_data

    def calc_volume_metrics(self, df):
        # calculate stats
        df = self.calc_volume_osc(df)
        # df = self.calc_volume_roc(df)

        return df

    def calc_volume_roc(self, df):
        # VOL_ROC = ( ( current_vol / vol_n_windows_back ) - 1 ) / 100
        return df

    def calc_volume_osc(self, df):
        # PVO = ( ( short_vol_ema - long_vol_ema ) / long_vol_ema ) * 100

        # cutoff tail, sized by window
        tail = df.tail(2).reset_index(drop=True)

        # drop last row, will be replaced after calculation
        df = df.drop(df.index[-1:])

        # calculate short EMA
        tail = self.set_ema(tail, 'SHORT_VOL_EMA', self.short_vol_ema_window, self.stat_key)

        # calculate long EMA
        tail = self.set_ema(tail, 'LONG_VOL_EMA', self.long_vol_ema_window, self.stat_key)

        # calculate PVO
        pvo = ((tail.loc[1, 'SHORT_VOL_EMA'] - tail.loc[1, 'LONG_VOL_EMA']) / tail.loc[1, 'LONG_VOL_EMA']) * 100
        tail.set_value(1, 'PVO', pvo)

        # if we have calculated enough PVO's, start calculating the PVO_EMA
        # else calculate PVO_SMA
        if len(df) >= self.long_vol_ema_window + self.pvo_ema_window:
            self.is_active = True
            # calculate PVO EMA
            tail = self.set_ema(tail, 'PVO_EMA', self.pvo_ema_window, 'PVO')
            return df.append(tail.tail(1), ignore_index=True)
        else:
            df = df.append(tail.tail(1), ignore_index=True)
            df['PVO_EMA'] = df['PVO'].rolling(window=self.pvo_ema_window, center=False).mean()
            return df

    def set_ema(self, df, ema_key, ema_window, stat_key):
        prev_ema = df.loc[0, ema_key]
        next_ema = self.calc_ema(df, ema_window, prev_ema, stat_key)
        df.set_value(1, ema_key, next_ema)
        return df

    @staticmethod
    def calc_ema(df, window, prev_ema, stat_key):
        # EMA = (last - prev_ema) * multiplier + prev_ema
        multiplier = 2.0 / (window + 1)
        return (df.loc[1, stat_key] - prev_ema) * multiplier + prev_ema

    def get_mkt_report(self, mkt_name, mkt_data):
        # get standard report data
        report = self._get_mkt_report(mkt_name, mkt_data)

        # calculate:
        # 1) % change over most recent window
        # 2) % change over most recent tick
        tail = mkt_data.tail(self.window).reset_index(drop=True)
        tick_volume = tail.loc[self.window - 1, self.stat_key]
        prev_tick_volume = tail.loc[self.window - 2, self.stat_key]
        window_volume = tail.loc[0, self.stat_key]
        window_pct_change = 100 * (tick_volume - window_volume) / window_volume
        last_tick_pct_change = 100 * (tick_volume - prev_tick_volume) / window_volume
        window_pct_change_str = "% change over window: " + str(window_pct_change) + "%"
        last_tick_pct_change_str = "% change over tick: " + str(last_tick_pct_change) + "%"

        report['strat_specific_data'] = window_pct_change_str + "\n" + last_tick_pct_change_str + "\n"
        return report
