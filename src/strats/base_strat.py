import os
from src.utils.logger import Logger

log = Logger(__name__)

class BaseStrategy:
    def __init__(self, options):
        self.name = options['name']
        self.plot_overlay = options['plot_overlay']
        self.active = options['active']
        self.stat_key = options['stat_key']
        self.window = options['window']
        self.ema_window = options['ema_window']
        self.buy_positions = {}
        self.sell_positions = {}
        self.ema_suffix = '_EMA'
        self.pct_weight_suffix = '_PCT_WEIGHT'

    def init_market_positions(self, pairs):
        self.buy_positions = {pair: False for pair, p in pairs.items()}
        self.sell_positions = {pair: False for pair, p in pairs.items()}

    def handle_data(self, mkt_data, pair):
        raise Exception('HANDLE_DATA function should be overwritten')

    def should_buy(self, pair):
        return self.buy_positions[pair['pair']]

    def should_sell(self, pair):
        return self.sell_positions[pair['pair']]

    def get_mkt_report(self, pair, mkt_data):
        return self._get_mkt_report(pair['pair'], mkt_data)

    def _get_mkt_report(self, pair, mkt_data):
        mkt_report = dict(strat_name=self.name, window=self.window)
        mkt_report['recent_data'] = mkt_data.tail(self.window * 10)
        if self.buy_positions[pair['pair']]:
            mkt_report['action'] = 'BUY'
        elif self.sell_positions[pair['pair']]:
            mkt_report['action'] = 'SELL'
        return mkt_report

    def _set_positions(self, buy, sell, pair):
        self.buy_positions[pair['pair']] = buy
        self.sell_positions[pair['pair']] = sell
        if buy:
            log.info(' * * * BUY :: ' + pair)
        elif sell:
            log.info(' * * * SELL :: ' + pair)
        else:
            log.debug(' * * * HOLD :: ' + pair)
