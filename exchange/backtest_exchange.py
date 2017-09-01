from db.psql import PostgresConnection
from utils import get_coins_from_market, normalize_inf_rows
import pandas as pd
from logger import Logger
log = Logger(__name__)

class BacktestExchange:
    def __init__(self, start_date, end_date):
        log.info('Initializing backtest exchange...')
        self.start_date = start_date
        self.end_date = end_date
        self.psql = PostgresConnection()
        self.balances = {
            'USD': 20000,
            'BTC': 3
        }
        self.starting_balances = self.balances.copy()
        self.trades = {
            'USD-BTC': []
        }
        self.tick = -1
        self.market_summaries = self.load_market_summaries()
        log.info('backtest exchange successfully initialized')

    def load_market_summaries(self):
        data = self.psql.get_historical_data(self.start_date, self.end_date)
        length = len(data)
        mkt_name_series = pd.Series(['USD-BTC'] * length)
        data = data.assign(MarketName=mkt_name_series.values)
        data = data.assign(Last=data['close'].values)
        data = normalize_inf_rows(data)
        summary = {'USD-BTC': data}
        return summary

    def update_buy_balances(self, market, quantity, rate):
        base_coin, mkt_coin = get_coins_from_market(market)
        self.balances[base_coin] -= (quantity * rate)
        self.balances[mkt_coin] += quantity

    def update_sell_balances(self, market, quantity, rate):
        base_coin, mkt_coin = get_coins_from_market(market)
        self.balances[base_coin] += (quantity * rate)
        self.balances[mkt_coin] -= quantity

    def getmarkets(self):
        return [
            {
                "MarketCurrency": "USD",
                "BaseCurrency": "BTC",
                "MarketCurrencyLong": "USDollars",
                "BaseCurrencyLong": "Bitcoin",
                "MinTradeSize": 0.01000000,
                "MarketName": "USD-BTC",
                "IsActive": True,
                "Created": "2014-02-13T00:00:00"
            }
        ]

    def getcurrencies(self):
        return [
            {
                "Currency" : "BTC",
                "CurrencyLong" : "Bitcoin",
                "MinConfirmation" : 2,
                "TxFee" : 0.00020000,
                "IsActive" : True,
                "CoinType" : "BITCOIN",
                "BaseAddress" : ''
            }
        ]

    def getticker(self, market):
        summary = self.market_summaries[market].loc[self.tick]
        return [summary]

    def getmarketsummaries(self):
        self.tick += 1
        summary = self.market_summaries['USD-BTC'].loc[self.tick]
        return [summary]

    # def getmarketsummary(self, market):
    #     return self.query('getmarketsummary', {'market': market})
    #
    # def getorderbook(self, market, type, depth=20):
    #     return self.query('getorderbook', {'market': market, 'type': type, 'depth': depth})
    #
    # def getmarkethistory(self, market, count=20):
    #     return self.query('getmarkethistory', {'market': market, 'count': count})
    #
    def buylimit(self, market, quantity, rate):
        trade = {'order_type': 'buy', 'market': market, 'quantity': quantity, 'rate': rate}
        self.update_buy_balances(market, quantity, rate)
        return self.trades[market].append(trade)
    #
    # # DEPRECATED
    # # def buymarket(self, market, quantity):
    # #     return self.query('buymarket', {'market': market, 'quantity': quantity})
    #
    def selllimit(self, market, quantity, rate):
        trade = {'order_type': 'sell', 'market': market, 'quantity': quantity, 'rate': rate}
        self.update_sell_balances(market, quantity, rate)
        return self.trades[market].append(trade)
    #
    # # DEPRECATED
    # # def sellmarket(self, market, quantity):
    # #     return self.query('sellmarket', {'market': market, 'quantity': quantity})
    #
    # def cancel(self, uuid):
    #     return self.query('cancel', {'uuid': uuid})
    #
    # def getopenorders(self, market):
    #     return self.query('getopenorders', {'market': market})

    def getbalances(self):
        return self.balances

    def getbalance(self, currency):
        return self.balances[currency]
    #
    # def getdepositaddress(self, currency):
    #     return self.query('getdepositaddress', {'currency': currency})
    #
    # def withdraw(self, currency, quantity, address):
    #     return self.query('withdraw', {'currency': currency, 'quantity': quantity, 'address': address})
    #
    # def getorder(self, uuid):
    #     return self.query('getorder', {'uuid': uuid})
    #
    # def getorderhistory(self, market, count):
    #     return self.query('getorderhistory', {'market': market, 'count': count})
    #
    # def getwithdrawalhistory(self, currency, count):
    #     return self.query('getwithdrawalhistory', {'currency': currency, 'count': count})
    #
    # def getdeposithistory(self, currency, count):
    #     return self.query('getdeposithistory', {'currency': currency, 'count': count})
