from backtest_exchange import BacktestExchange
from bittrex import Bittrex
import os


class ExchangeFactory:
    def get_exchange(self):
        if os.getenv('TESTING', 'FALSE') == 'TRUE':
            return BacktestExchange
        else:
            return Bittrex