import datetime
import json
import urllib
from datetime import timedelta
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from src.db.psql import PostgresConnection
from src.utils.logger import Logger
from src.utils.utils import is_valid_market, normalize_inf_rows_dicts, add_saved_timestamp, normalize_index

log = Logger(__name__)

MAX_BTC_PER_BUY = 0.05
BUY_DECREMENT_COEFFICIENT = 0.75
MAJOR_TICK_SIZE = 15
SMA_WINDOW = 20
EXECUTE_TRADES = False
TESTING = False
if TESTING:
    BASE_CURRENCIES = ['USD', 'BTC']
else:
    BASE_CURRENCIES = ['BTC', 'ETH']
TESTING_START_DATE = datetime.datetime(2017, 1, 1)
TESTING_END_DATE = datetime.datetime(2017, 8, 31)

bb_options = {
    'active': True,
    'market_names': [],
    'num_standard_devs': 2,
    'sma_window': SMA_WINDOW,
    'sma_stat_key': 'close',
    'minor_tick': 1,
    'major_tick': MAJOR_TICK_SIZE,
    'testing': TESTING
}


class CryptoBot:
    def __init__(self, strat, exchange):
        log.info('Initializing bot...')
        self.psql = PostgresConnection()
        self.strat = strat
        self.btrx = exchange
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
        self.major_tick = 0
        bb_options['market_names'] = list(map(lambda market: market['MarketName'], self.markets))
        log.info('bot successfully initialized')

    def init_markets(self):
        self.currencies = self.btrx.getcurrencies()
        self.markets = self.get_markets()
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
            if self.check_major_tick():
                self.major_tick_step()
                self.execute_trades()

    def run_test(self):
        while (True):
            self.tick_step()

        self.analyze_performance()


        ## QUANT ##

    def tick_step(self):
        self.minor_tick_step()
        if self.check_major_tick():
            log.info('MAJOR TICK')
            self.major_tick_step()
            self.execute_trades()

    def minor_tick_step(self):
        self.increment_minor_tick()
        # get the ticker for all the markets
        summaries = self.get_market_summaries()
        for summary in summaries:
            mkt_name = summary['marketname']
            if is_valid_market(mkt_name, BASE_CURRENCIES) and mkt_name in self.summary_tickers:
                self.summary_tickers[mkt_name] = self.summary_tickers[mkt_name].append(summary, ignore_index=True)
                # if not TESTING:
                #     self.summary_tickers[mkt_name] = ohlc_hack(self.summary_tickers[mkt_name])

    def major_tick_step(self):
        self.increment_major_tick()
        self.strat.handle_data(self.summary_tickers, self.major_tick)


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
                log.warning('Rate Limit :: sleeping for ' + str(sleep_for) + ' seconds')
                sleep(sleep_for.seconds)
                self.rate_limiter_reset()


        ## TICKER ##

    def increment_minor_tick(self):
        self.tick += 1

    def increment_major_tick(self):
        self.major_tick += 1

    def check_major_tick(self):
        return (self.tick % MAJOR_TICK_SIZE) == 0


        ## MARKET ##

    def get_market_summaries(self):
        log.info('== GET market summaries ==')
        return self.btrx.getmarketsummaries()

    def get_market_history(self, market):
        log.info('== GET market history ==')
        return self.btrx.getmarkethistory(market)

    def get_order_book(self, market, order_type, depth):
        log.info('== GET order book ==')
        return self.btrx.getorderbook(market, order_type, depth)

    def get_ticker(self, market):
        log.info('== GET ticker ==')
        return self.btrx.getticker(market)

    def get_markets(self):
        log.info('== GET markets ==')
        return self.btrx.getmarkets()


        ## ORDERS ##

    def calculate_num_coins(self, order_type, market, quantity):
        coins = market.split('-')
        if order_type == 'buy':
            coin = coins[0]
        elif order_type == 'sell':
            coin = coins[1]
        else:
            raise Exception('order type must be buy or sell but was ' + order_type)
        balance = self.get_balance(coin)
        return balance * quantity

    def calculate_order_rate(self, market, order_type, quantity, order_book_depth):
        if TESTING:
            return self.btrx.get_order_rate(market, self.tick)
        else:
            order_book = self.get_order_book(market, order_type, order_book_depth)
            current_total = 0
            rate = 0
            # calculate an instant price
            for order in order_book:
                current_total += order['quantity']
                rate = order['rate']
                if current_total >= quantity:
                    break
            return rate

    def buy_instant(self, market, quantity):
        log.info('== BUY instant ==')
        self.trade_instant('buy', market, quantity)

    def sell_instant(self, market, quantity):
        log.info('== SELL instant ==')
        self.trade_instant('sell', market, quantity)

    def trade_instant(self, order_type, market, pct_holdings):
        quantity = self.calculate_num_coins(order_type, market, pct_holdings)
        try:
            rate = self.calculate_order_rate(market, order_type, quantity, 20)
            if EXECUTE_TRADES:
                trade_resp = self.trades[order_type](market, quantity, rate)
            if trade_resp and not isinstance(trade_resp, basestring):
                self.trade_success(order_type, market, quantity, rate, trade_resp['uuid'])
                return trade_resp
            else:
                log.info(trade_resp)
                return None
        except Exception as e:
            log.error("*** !!! TRADE FAILED !!! ***")
            log.error(e)
            return None

    def buy_market(self, market, quantity):
        log.info('== BUY market ==')
        self.trade_market('buy', market, quantity)

    def sell_market(self, market, quantity):
        log.info('== SELL market ==')
        self.trade_market('sell', market, quantity)

    def trade_market(self, order_type, market, pct_holdings):
        quantity = self.calculate_num_coins(order_type, market, pct_holdings)
        try:
            ticker = self.btrx.getticker(market)
            rate = ticker['last']
            if EXECUTE_TRADES:
                trade_resp = self.trades[order_type](market, quantity, rate)
            if trade_resp and not isinstance(trade_resp, basestring):
                self.trade_success(order_type, market, quantity, rate, trade_resp['uuid'])
                return trade_resp
            else:
                log.info(trade_resp)
                return None
        except Exception as e:
            log.error("*** !!! TRADE FAILED !!! ***")
            log.error(e)
            return None

    def CANCEL(self, uuid):
        log.info('== CANCEL bid ==')
        try:
            trade_resp = self.btrx.cancel(uuid)
            self.psql.save_trade('CANCEL', 'market', 0, 0, trade_resp['uuid'])
            return trade_resp
        except Exception as e:
            log.error("*** !!! TRADE FAILED !!! ***")
            log.error(e)
            return None

    def trade_success(self, order_type, market, quantity, rate, uuid):
        self.psql.save_trade(order_type, market, quantity, rate, uuid)
        log.info('*** ' + order_type.upper() + ' Successful! ***')
        log.info('market: ' + market + ' :: ' + 'quantity: ' + quantity + ' :: ' + 'rate: ' + rate + ' :: ' + 'trade id: ' + uuid)

    def execute_trades(self):
        for market in self.markets:
            mkt_name = market['marketname']
            if self.strat.should_buy(mkt_name):
                self.buy_instant(mkt_name, .1)
            elif self.strat.should_sell(mkt_name):
                self.sell_instant(mkt_name, 1)


        ## ACCOUNT ##

    def get_balances(self):
        log.info('== GET balances ==')
        balances = self.btrx.getbalances()
        return balances

    def get_balance(self, currency):
        log.info('== GET balance ==')
        balance = self.btrx.getbalance(currency)
        return balance

    def get_order_history(self, market, count):
        log.info('== GET order history ==')
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
                log.info('Collecting order book for: ' + market_name)
                order_book = self.get_order_book(market_name, 'both', 50)
                order_books[market_name].append(order_book)
            self.rate_limiter_limit()


        # BITTREX MARKET DATA COLLECTOR #

    def collect_summaries(self):
        self.rate_limiter_reset()
        while True:
            summaries = self.get_market_summaries()
            summaries = add_saved_timestamp(summaries, self.tick)
            self.psql.save_summaries(summaries)
            self.rate_limiter_limit()
            self.tick += 1

    def collect_markets(self):
        markets = self.get_markets()
        results = []
        for market in markets:
            market_data = normalize_index(pd.Series(market))
            market_data.drop(['created'], inplace=True)
            results.append(market_data)
        self.psql.save_markets(results)

        # HISTORICAL BTC DATA SCRAPER FOR bitcoincharts.com

    def get_historical_data(self):
        endpoint = 'https://bitcoincharts.com/charts/chart.json?m=bitstampUSD&SubmitButton=Draw&r=2&i=1-min&c=1&s='
        start_date = datetime.datetime(2017, 2, 8)
        current_date = start_date
        end_date = datetime.datetime(2017, 8, 24)

        while current_date.date() < end_date.date():
            sleep(3)
            next_date = current_date + timedelta(days=1)
            cd = current_date.strftime('%Y-%m-%d')
            nd = next_date.strftime('%Y-%m-%d')
            log.info('** getting BTC historical data ** ' + cd + ' :: ' + nd)
            url = endpoint + cd + '&e=' + nd + '&Prev=&Next=&t=S&b=&a1=&m1=10&a2=&m2=25&x=0&i1=&i2=&i3=&i4=&v=1&cv=0&ps=0&l=0&p=0&'
            resp = urllib.urlopen(url)
            html = resp.read()
            bs = BeautifulSoup(html, 'html.parser')
            try:
                data = json.loads(bs.contents[0])
                data = normalize_inf_rows_dicts(data)
                self.psql.save_historical_data(data)
            except Exception as e:
                log.error(e)
            current_date = current_date + timedelta(days=1)


        ## BACKTESTING TOOLS ##

    def analyze_performance(self):
        starting_balances = self.btrx.starting_balances
        current_balances = self.btrx.getbalances()
        log.info('*** PERFORMANCE RESULTS ***')
        for currency in starting_balances:
            start = starting_balances[currency]
            end = current_balances[currency]
            log.info(' == ' + currency + ' == ')
            log.info('Start    :: ' + str(start))
            log.info('End      :: ' + str(end))
            log.info('% diff   :: ' + str((end - start) / start))
