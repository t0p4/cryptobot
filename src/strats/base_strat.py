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
        self.buy_positions = {}
        self.sell_positions = {}

    def init_market_positions(self, markets):
        self.buy_positions = {mkt_name: False for mkt_name in markets['marketname']}
        self.sell_positions = {mkt_name: False for mkt_name in markets['marketname']}

    def handle_data(self, mkt_data, mkt_name):
        raise Exception('HANDLE_DATA function should be overwritten')

    def should_buy(self, mkt_name):
        return self.buy_positions[mkt_name]

    def should_sell(self, mkt_name):
        return self.sell_positions[mkt_name]

    def get_mkt_report(self, mkt_name, mkt_data):
        return self._get_mkt_report(mkt_name, mkt_data)

    def _get_mkt_report(self, mkt_name, mkt_data):
        mkt_report = {'strat_name': self.name, 'window': self.window}
        mkt_report['recent_data'] = mkt_data.tail(self.window * 10)
        if self.buy_positions[mkt_name]:
            mkt_report['action'] = 'BUY'
        elif self.sell_positions[mkt_name]:
            mkt_report['action'] = 'SELL'
        return mkt_report

    def _set_positions(self, buy, sell, mkt_name):
        self.buy_positions[mkt_name] = buy
        self.sell_positions[mkt_name] = sell
        if buy:
            log.info(' * * * BUY :: ' + mkt_name)
        elif sell:
            log.info(' * * * SELL :: ' + mkt_name)
        else:
            log.debug(' * * * HOLD :: ' + mkt_name)
