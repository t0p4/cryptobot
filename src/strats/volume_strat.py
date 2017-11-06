import pandas as pd
from base_strat import BaseStrategy
from src.utils.logger import Logger
log = Logger(__name__)


class VolumeStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.sma_window = options['sma_window']
        self.major_tick = options['major_tick']

    def handle_data(self, data, major_tick):
        log.info('Stochastic RSI Strat :: handle_data')
        for mkt_name, mkt_data in data.iteritems():
            if len(mkt_data) >= self.major_tick:
                mkt_data = self.calc_stochastic_rsi(mkt_data)
                if current_tick_buy and prev_tick_sell:
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

    def calc_volume_osc(self, df):
        return df
