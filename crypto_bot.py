from bittrex import bittrex
from secrets import BITTREX_API_KEY, BITTREX_API_SECRET
from db.psql import PostgresConnection
from utils import is_valid_market
import pandas as pd
import datetime
from time import sleep

MAX_BTC_PER_BUY = 0.05
BUY_DECREMENT_COEFFICIENT = 0.75
BASE_CURRENCIES = ['BTC', 'ETH']
TICK_SIZE = 20
EXECUTE_TRADES = False

class CryptoBot:
    def __init__(self):
        self.psql = PostgresConnection()
        self.btrx = bittrex(BITTREX_API_KEY, BITTREX_API_SECRET)
        self.trades = {'buy': self.btrx.buylimit, 'sell': self.btrx.selllimit}
        self.RATE_LIMIT = datetime.timedelta(0, 60, 0)
        self.api_tick = datetime.datetime.now()
        self.currencies = []
        self.summary_tickers = {}
        self.markets = []
        self.init_markets()
        self.markets_to_watch = []
        self.balances = self.get_balances()
        self.accounts = []
        self.tick = 0

    def init_markets(self):
        self.currencies = self.btrx.getcurrencies()
        self.markets = self.btrx.getmarkets()
        for market in self.markets:
            mkt_name = market['MarketName']
            self.summary_tickers[mkt_name] = pd.DataFrame()


        ## RATE LIMITER ##

    def rate_limiter_start(self):
        self.api_tick = datetime.datetime.now()

    def rate_limiter_check(self):
        current_tick = datetime.datetime.now()
        return (current_tick - self.api_tick) >= self.RATE_LIMIT

    def rate_limiter_limit(self):
        current_tick = datetime.datetime.now()
        sleep_for = current_tick - self.api_tick
        sleep(sleep_for.seconds)


        ## TICKER ##

    def increment_tick(self):
        if self.check_tick():
            self.tick = 1
        else:
            self.tick += 1

    def check_tick(self):
        return self.tick == TICK_SIZE


        ## MARKET ##

    def get_market_summaries(self):
        return self.btrx.getmarketsummaries()

    def get_market_history(self, market):
        return self.btrx.getmarkethistory(market)

    def get_order_book(self, market, order_type, depth):
        return self.btrx.getorderbook(market, order_type, depth)

    def get_ticker(self, market):
        return self.btrx.getticker(market)

        ## ORDERS ##

    def buy_instant(self, market, quantity):
        self.trade_instant('buy', market, quantity)

    def sell_instant(self, market, quantity):
        self.trade_instant('sell', market, quantity)

    def trade_instant(self, order_type, market, quantity):
        try:
            order_book = self.get_order_book(market, order_type, 20)
            current_total = 0
            rate = 0
            # calculate an instant buy price
            for order in order_book:
                current_total += order['Quantity']
                rate = order['Rate']
                if current_total >= quantity:
                    break

            trade_resp = self.trades[order_type](market, quantity, rate)
            if not isinstance(trade_resp, basestring):
                self.trade_success(order_type, market, quantity, rate, trade_resp['uuid'])
                return trade_resp
            else:
                print trade_resp
                return None
        except Exception as e:
            print("*** !!! TRADE FAILED !!! ***")
            print(e)
            return None

    def buy_market(self, market, quantity):
        self.trade_market('buy', market, quantity)

    def sell_market(self, market, quantity):
        self.trade_market('sell', market, quantity)

    def trade_market(self, order_type, market, quantity):
        try:
            ticker = self.btrx.getticker(market)
            rate = ticker['Last']
            trade_resp = self.trades[order_type](market, quantity, rate)
            if not isinstance(trade_resp, basestring):
                self.trade_success(order_type, market, quantity, rate, trade_resp['uuid'])
                return trade_resp
            else:
                print trade_resp
                return None
        except Exception as e:
            print("*** !!! TRADE FAILED !!! ***")
            print(e)
            return None

    def CANCEL(self, uuid):
        try:
            trade_resp = self.btrx.cancel(uuid)
            self.psql.save_trade('CANCEL', 'market', 0, 0, trade_resp['uuid'])
            return trade_resp
        except Exception as e:
            print("*** !!! TRADE FAILED !!! ***")
            print(e)
            return None

    def trade_success(self, order_type, market, quantity, rate, uuid):
        self.psql.save_trade(order_type, market, quantity, rate, uuid)
        print('*** ' + order_type.upper() + ' Successful! ***')
        print('market: ' + market)
        print('quantity: ' + quantity)
        print('rate: ' + rate)
        print('trade id: ' + uuid)


        ## ACCOUNT ##

    def get_balances(self):
        balances = self.btrx.getbalances()
        return balances

    def get_balance(self, currency):
        balance = self.btrx.getbalance(currency)
        return balance

    def get_order_history(self, market, count):
        history = self.btrx.getorderhistory(market, count)
        return history


        ## QUANT ##

    def tick(self):
        self.increment_tick()
        # get the ticker for all the markets
        summaries = self.get_market_summaries()
        for summary in summaries:
            mkt_name = summary.MarketName
            if is_valid_market(mkt_name, BASE_CURRENCIES):
                self.summary_tickers[mkt_name].append(summary)
                self.summary_tickers[mkt_name] = self.calc_bollinger_bounds(self.summary_tickers[mkt_name])
                if summary['Last'] >= self.summary_tickers[mkt_name]['UPPER_BB']:
                    if not self.markets_to_watch[mkt_name]:
                        self.markets_to_watch[mkt_name] = True
                    else:
                        buy_quantity = summary['Last'] / MAX_BTC_PER_BUY
                        self.BUY_market(mkt_name, buy_quantity)

    def calc_bollinger_bounds(self, df):
        df['MA20'] = pd.stats.moments.rolling_mean(df['Last'], TICK_SIZE)
        df['STDDEV'] = pd.stats.moments.rolling_std(df['Last'], TICK_SIZE)
        df['UPPER_BB'] = df['MA20'] + 2 * df['STDDEV']
        df['LOWER_BB'] = df['MA20'] - 2 * df['STDDEV']