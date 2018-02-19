from src.exchange.backtest_exchange import BacktestExchange
from src.exchange.bittrex import Bittrex
import os


class ExchangeFactory:
    def get_exchange(self):
        if os.getenv('BACKTESTING', 'FALSE') == 'TRUE':
            return BacktestExchange
        else:
            return Bittrex