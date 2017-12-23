import os


class BaseStrategy:
    def __init__(self, options):
        self.name = options['name']
        self.plot_overlay = options['plot_overlay']
        self.active = options['active']
        self.window = options['window']
        self.buy_positions = {}
        self.sell_positions = {}
        self.BACKTESTING = os.getenv('BACKTESTING', 'FALSE')

    def init_market_positions(self, markets):
        self.buy_positions = {mkt_name: False for mkt_name in markets['marketname']}
        self.sell_positions = {mkt_name: False for mkt_name in markets['marketname']}

    def handle_data(self, data, tick):
        raise Exception('HANDLE_DATA function should be overwritten')

    def should_buy(self, mkt_name):
        return self.buy_positions[mkt_name]

    def should_sell(self, mkt_name):
        return self.sell_positions[mkt_name]

    def _get_mkt_report(self, mkt_name, mkt_data):
        mkt_report = {'strat_name': self.name, 'window': self.window}
        mkt_report['recent_data'] = str(mkt_data.tail(self.window))
        if self.buy_positions[mkt_name]:
            mkt_report['action'] = 'BUY'
        elif self.sell_positions[mkt_name]:
            mkt_report['action'] = 'SELL'
        return mkt_report

    def get_mkt_report(self, mkt_name, mkt_data):
        return self._get_mkt_report(mkt_name, mkt_data)
