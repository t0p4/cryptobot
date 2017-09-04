from backtest_exchange import BacktestExchange
from bittrex import Bittrex


class ExchangeFactory:
    def get_exchange(self, testing):
        if testing:
            return BacktestExchange
        else:
            return Bittrex