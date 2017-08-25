class BaseStrategy:
    def __init__(self, options):
        self.active = options['active']
        self.buy_positions = {mkt_name: False for mkt_name in options['market_names']}
        self.sell_positions = {mkt_name: False for mkt_name in options['market_names']}

    def handle_data(self, data, tick):
        raise Exception('HANDLE_DATA function should be overwritten')

    def should_buy(self, mkt_name):
        return self.buy_positions[mkt_name]

    def should_sell(self, mkt_name):
        return self.sell_positions[mkt_name]