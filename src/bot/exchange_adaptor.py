from src.exchange.binance.client import Client
from src.exchange.bittrex import Bittrex
from src.exchange.backtest_exchange import BacktestExchange
from src.exchange.coinigy.coinigy_api_rest import CoinigyREST
from src.exchange.gemini import Geminipy
import pandas as pd
from src.utils.conversion_utils import convert_str_columns_to_num


class ExchangeAdaptor:
    def __init__(self):
        self.exchange_adaptors = {
            'binance': Client,
            'bittrex': Bittrex,
            'coinigy': CoinigyREST,
            'backtest': BacktestExchange,
            'gemini': Geminipy
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
        elif exchange == 'coinigy':
            balances = ex_adaptor.balances()
            coinigy_col_keys = ['balance_amount_avail', 'balance_amount_held', 'balance_amount_total', 'btc_balance', 'last_price']
            return convert_str_columns_to_num(pd.DataFrame(balances), coinigy_col_keys)
        else:
            return {}

    def get_btc_usd_rate(self):
        ex = self.exchange_adaptors['gemini']()
        ticker = ex.pubticker('btcusd')
        return float(ticker['last'])

    def get_eth_usd_rate(self):
        ex = self.exchange_adaptors['gemini']()
        ticker = ex.pubticker('ethusd')
        return float(ticker['last'])
