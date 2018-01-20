from src.exchange.binance.client import Client
from src.exchange.bittrex import Bittrex
from src.exchange.backtest_exchange import BacktestExchange
import pandas as pd

class ExchangeAdaptor:
    def __init__(self):
        self.exchange_adaptors = {
            'binance': Client,
            'bittrex': Bittrex,
            'backtest': BacktestExchange
        }

    def get_exchange_adaptor(self, exchange):
        return self.exchange_adaptors[exchange]()

    def get_exchange_balances(self, exchange):
        ex_adaptor = self.get_exchange_adaptor(exchange)
        if exchange == 'binance':
            account = ex_adaptor.get_account({'recvWindow': 10000})
            result = []
            for balance in account['balances']:
                result.append({'currency': balance['asset'], 'balance': balance['free']})
            return pd.DataFrame(result)
        else:
            return {}
