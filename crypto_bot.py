import datetime
import json
import urllib
from datetime import timedelta
from time import sleep

import pandas as pd
from bs4 import BeautifulSoup

from db.psql import PostgresConnection
from exchange.bittrex import bittrex
from secrets import BITTREX_API_KEY, BITTREX_API_SECRET
from utils import is_valid_market
from exchange.exchange_factory import ExchangeFactory

MAX_BTC_PER_BUY = 0.05
BUY_DECREMENT_COEFFICIENT = 0.75
BASE_CURRENCIES = ['BTC', 'ETH']
MAJOR_TICK_SIZE = 15
EXECUTE_TRADES = False
TESTING = True
TESTING_START_DATE = datetime.datetime(2015, 1, 1)
TESTING_END_DATE = datetime.datetime(2015, 1, 5)

bb_options = {
    'active': True,
    'market_names': [],
    'num_standard_devs': 2,
    'sma_window': 15,
    'sma_stat_key': 'Low',
    'minor_tick': 1,
    'major_tick': 15
}

class CryptoBot:
    def __init__(self, strat):
        self.psql = PostgresConnection()
        if TESTING:
            self.btrx = ExchangeFactory().get_exchange(TESTING)(TESTING_START_DATE, TESTING_END_DATE)
        else:
            self.btrx = ExchangeFactory().get_exchange(TESTING)(BITTREX_API_KEY, BITTREX_API_SECRET)
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
        bb_options['market_names'] = list(map(lambda market: market['MarketName'], self.markets))
        self.strat = strat(bb_options)

    def init_markets(self):
        self.currencies = self.btrx.getcurrencies()
        self.markets = self.btrx.getmarkets()
        for market in self.markets:
            mkt_name = market['MarketName']
            self.summary_tickers[mkt_name] = pd.DataFrame()

    def run(self):
        if TESTING:
            self.run_test()
        else:
            self.run_prod()

    def run_prod(self):
        while (True):
            self.rate_limiter_limit()
            self.minor_tick_step()
            self.execute_trades()

    def run_test(self):
        while (True):
            self.tick_step()

        self.analyze_performance()

        ## QUANT ##

    def tick_step(self):
        self.minor_tick_step()
        if self.major_tick():
            self.major_tick_step()
            self.execute_trades()

    def minor_tick_step(self):
        self.increment_tick()
        # get the ticker for all the markets
        summaries = self.get_market_summaries()
        for summary in summaries:
            idx = summary.first_valid_index()
            mkt_name = summary['MarketName'][idx]
            if is_valid_market(mkt_name, BASE_CURRENCIES):
                self.summary_tickers[mkt_name].append(summary)

    def major_tick_step(self):
        self.strat.handle_data(self.summary_tickers, self.tick)

        ## RATE LIMITER ##

    def rate_limiter_reset(self):
        self.api_tick = datetime.datetime.now()

    def rate_limiter_check(self):
        current_tick = datetime.datetime.now()
        return (current_tick - self.api_tick) < self.RATE_LIMIT

    def rate_limiter_limit(self):
        if not TESTING:
            current_tick = datetime.datetime.now()
            if self.rate_limiter_check():
                sleep_for = self.RATE_LIMIT - (current_tick - self.api_tick)
                print('[WARNING] Rate Limit :: sleeping for ' + str(sleep_for) + ' seconds')
                sleep(sleep_for.seconds)
                self.rate_limiter_reset()


        ## TICKER ##

    def increment_tick(self):
        self.tick += 1

    def major_tick(self):
        return (self.tick % MAJOR_TICK_SIZE) == 0

        ## MARKET ##

    def get_market_summaries(self):
        print('== GET market summaries ==')
        return self.btrx.getmarketsummaries()

    def get_market_history(self, market):
        print('== GET market history ==')
        return self.btrx.getmarkethistory(market)

    def get_order_book(self, market, order_type, depth):
        print('== GET order book ==')
        return self.btrx.getorderbook(market, order_type, depth)

    def get_ticker(self, market):
        print('== GET ticker ==')
        return self.btrx.getticker(market)

        ## ORDERS ##

    def buy_instant(self, market, quantity):
        print('== BUY instant ==')
        self.trade_instant('buy', market, quantity)

    def sell_instant(self, market, quantity):
        print('== SELL instant ==')
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
        print('== BUY market ==')
        self.trade_market('buy', market, quantity)

    def sell_market(self, market, quantity):
        print('== SELL market ==')
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
        print('== CANCEL bid ==')
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

    def execute_trades(self):
        for market in self.markets:
            mkt_name = market['MarketName']
            if self.strat.should_buy(mkt_name):
                self.buy_instant(mkt_name, .1)
            elif self.strat.should_sell(mkt_name):
                self.sell_instant(mkt_name)

        ## ACCOUNT ##

    def get_balances(self):
        print('== GET balances ==')
        balances = self.btrx.getbalances()
        return balances

    def get_balance(self, currency):
        print('== GET balance ==')
        balance = self.btrx.getbalance(currency)
        return balance

    def get_order_history(self, market, count):
        print('== GET order history ==')
        history = self.btrx.getorderhistory(market, count)
        return history


        ## SANDBOX ###

    def collect_order_books(self):
        order_books = {}
        for market in self.markets:
            order_books[market['MarketName']] = []
        self.rate_limiter_reset()
        while True:
            for market in self.markets:
                market_name = market['MarketName']
                print('Collecting order book for: ' + market_name)
                order_book = self.get_order_book(market_name, 'both', 50)
                order_books[market_name].append(order_book)
            self.rate_limiter_limit()

    def collect_summaries(self):
        self.rate_limiter_reset()
        while True:
            summaries = self.get_market_summaries()
            self.psql.save_summaries(summaries)
            self.rate_limiter_limit()

    def get_historical_data(self):
        # HISTORICAL BTC DATA SCRAPER FOR bitcoincharts.com
        endpoint = 'https://bitcoincharts.com/charts/chart.json?m=bitstampUSD&SubmitButton=Draw&r=2&i=1-min&c=1&s='
        start_date = datetime.datetime(2015, 1, 1)
        current_date = start_date
        end_date = datetime.datetime(2017, 8, 24)

        while current_date.date() < end_date.date():
            next_date = current_date + timedelta(days=1)
            cd = current_date.strftime('%Y-%m-%d')
            nd = next_date.strftime('%Y-%m-%d')
            print('** getting BTC historical data ** ' + cd + ' :: ' + nd)
            url = endpoint + cd + '&e=' + nd + '&Prev=&Next=&t=S&b=&a1=&m1=10&a2=&m2=25&x=0&i1=&i2=&i3=&i4=&v=1&cv=0&ps=0&l=0&p=0&'
            resp = urllib.urlopen(url)
            html = resp.read()
            bs = BeautifulSoup(html)
            try:
                data = json.loads(bs.contents[0])
                self.psql.save_historical_data(data)
            except Exception as e:
                print(e)
            current_date = current_date + timedelta(days=1)

        ## BACKTESTING TOOLS ##
    def analyze_performance(self):
        starting_balances = self.btrx.starting_balances
        current_balances = self.btrx.getbalances()
        print('*** PERFORMANCE RESULTS ***')
        for currency in starting_balances:
            start = starting_balances[currency]
            end = current_balances[currency]
            print(' == ' + currency + ' == ')
            print('Start    :: ' + str(start))
            print('End      :: ' + str(end))
            print('% diff   :: ' + str((end - start) / start))
