import pandas as pd
from time import mktime
import datetime
from src.db.psql import PostgresConnection
from src.utils.logger import Logger
from src.utils.utils import get_coins_from_market, normalize_inf_rows, normalize_index

log = Logger(__name__)


class BacktestExchange:
    def __init__(self, start_date, end_date):
        log.info('Initializing backtest exchange...')
        self.start_date = start_date
        self.end_date = end_date
        self.psql = PostgresConnection()
        self.balances = self.init_balances()
        self.starting_balances = self.balances.copy()
        self.trades = {}
        self.tick = -1
        # self.market_summaries = self.load_market_summaries()
        log.info('backtest exchange successfully initialized')

    def init_balances(self):
        currencies = self.getcurrencies()
        balances = {}
        for currency in currencies['currency']:
            balances[currency] = 0
        balances['BTC'] = 20
        return balances

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
        return self.psql.get_fixture_markets()

    def getcurrencies(self):
        return self.psql.get_fixture_currencies()

    def getticker(self, market):
        return self.market_summaries[market].loc[self.tick]

    # def getmarketsummaries(self):
    #     self.tick += 1
    #     summary = self.market_summaries['USD-BTC'].loc[self.tick]
    #     return [summary]

    def getmarketsummaries(self):
        self.tick += 1
        summaries = self.psql.get_market_summaries_by_ticker(self.tick)
        results = []
        for idx, summary in summaries.iterrows():
            results.append(summary)
        return results

    # def getmarketsummary(self, market):
    #     return self.query('getmarketsummary', {'market': market})
    #
    # def getorderbook(self, market, type, depth=20):
    #     return self.query('getorderbook', {'market': market, 'type': type, 'depth': depth})

    def get_order_rate(self, market, tick):
        return self.market_summaries[market].loc[tick, 'Last']
    #
    # def getmarkethistory(self, market, count=20):
    #     return self.query('getmarkethistory', {'market': market, 'count': count})
    #

    def buylimit(self, market, quantity, rate):
        trade_uuid = mktime(datetime.datetime.now().timetuple())
        trade = {'order_type': 'buy', 'market': market, 'quantity': quantity, 'rate': rate, 'uuid': trade_uuid}
        self.update_buy_balances(market, quantity, rate)
        if self.trades[market]:
            self.trades[market].append(trade)
        else:
            self.trades[market] = [trade]
        return {'uuid': trade_uuid}

    def selllimit(self, market, quantity, rate):
        trade_uuid = mktime(datetime.datetime.now().timetuple())
        trade = {'order_type': 'sell', 'market': market, 'quantity': quantity, 'rate': rate, 'uuid': trade_uuid}
        self.update_sell_balances(market, quantity, rate)
        if self.trades[market]:
            self.trades[market].append(trade)
        else:
            self.trades[market] = [trade]
        return {'uuid': trade_uuid}

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
