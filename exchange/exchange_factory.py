from backtest_exchange import BacktestExchange
from bittrex import bittrex


class ExchangeFactory:
    def get_exchange(self, testing):
        if testing:
            return BacktestExchange
        else:
            return bittrex