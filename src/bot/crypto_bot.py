import os
import datetime
import json
import urllib
from datetime import timedelta
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from src.db.psql import PostgresConnection
from src.utils.utils import is_valid_market, normalize_inf_rows_dicts, add_saved_timestamp, normalize_index
from src.utils.logger import Logger
from src.exceptions import LargeLossError, TradeFailureError, InsufficientFundsError
from src.utils.emailer import Reporter
from src.utils.plotter import Plotter

MAX_CURRENCY_PER_BUY = {
    'BTC': .2,
    'ETH': 2
}

log = Logger(__name__)

MAJOR_TICK_SIZE = int(os.getenv('MAJOR_TICK_SIZE', 5))
EXECUTE_TRADES = False
BACKTESTING = os.getenv('BACKTESTING', 'FALSE')
ORDER_BOOK_DEPTH = 20


class CryptoBot:
    def __init__(self, strats, exchange):
        log.info('Initializing bot...')
        self.psql = PostgresConnection()
        self.strats = strats
        self.btrx = exchange
        self.trade_functions = {'buy': self.btrx.buylimit, 'sell': self.btrx.selllimit}
        self.base_currencies = os.getenv('BASE_CURRENCIES', 'BTC,ETH').split(',')
        self.tradeable_markets = self.init_tradeable_markets()
        self.tradeable_currencies = dict((m[4:], True) for m in os.getenv('TRADEABLE_MARKETS', 'BTC-LTC').split(','))
        self.completed_trades = {}
        self.rate_limit = datetime.timedelta(0, 60, 0)
        self.api_tick = datetime.datetime.now()
        self.currencies = []
        self.compressed_summary_tickers = {}
        self.summary_tickers = {}
        self.markets = None
        self.init_markets()
        self.markets_to_watch = []
        self.balances = self.get_balances()
        self.accounts = []
        self.tick = 1
        self.major_tick = 0
        self.reporter = Reporter()
        self.plotter = Plotter()
        log.info('...bot successfully initialized')

    def init_tradeable_markets(self):
        env_tradeable_markets = os.getenv('TRADEABLE_MARKETS', 'ALL')
        if env_tradeable_markets == 'ALL':
            return env_tradeable_markets
        else:
            return dict((m, True) for m in env_tradeable_markets.split(','))

    def init_markets(self):
        if BACKTESTING == 'TRUE':
            self.btrx.init_tradeable_markets(self.tradeable_markets)
        if os.getenv('COLLECT_FIXTURES', 'FALSE') != 'TRUE':
            self.currencies = self.get_currencies()
            self.markets = self.get_markets()
            for mkt_name in self.markets['marketname']:
                if is_valid_market(mkt_name, self.base_currencies):
                    self.compressed_summary_tickers[mkt_name] = pd.DataFrame()
                    self.summary_tickers[mkt_name] = pd.DataFrame()
            for strat in self.strats:
                strat.init_market_positions(self.markets)

    def run(self):
        if BACKTESTING:
            self.run_test()
        else:
            self.run_prod()

    def run_prod(self):
        log.info('* * * ! * * * BEGIN PRODUCTION RUN * * * ! * * *')
        while (True):
            self.rate_limiter_limit()
            self.tick_step()

    def run_test(self):
        log.info('* * * ! * * * BEGIN TEST RUN * * * ! * * *')
        while self.tick < 900:
            self.tick_step()

        self.cash_out()
        self.analyze_performance()

    def kill(self):
        log.warning('* * * ! * * * SHUTTING DOWN BOT * * * ! * * *')
        raise Exception

    def send_report(self, subj, body):
        self.reporter.send_report(subj, body)

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
            if is_valid_market(mkt_name, self.base_currencies) and mkt_name in self.summary_tickers:
                self.summary_tickers[mkt_name] = self.summary_tickers[mkt_name].append(summary, ignore_index=True)

    def major_tick_step(self):
        self.increment_major_tick()
        self.compress_tickers()
        for strat in self.strats:
            self.compressed_summary_tickers = strat.handle_data(self.compressed_summary_tickers, self.major_tick)

    def compress_tickers(self):
        for mkt_name, mkt_data in self.summary_tickers.iteritems():
            # tail = mkt_data.tail(MAJOR_TICK_SIZE).reset_index(drop=True)
            # mkt_data = mkt_data.drop(mkt_data.index[-MAJOR_TICK_SIZE:])
            agg_funcs = {'bid': ['last'], 'last': ['last'], 'ask': ['last'], 'marketname': ['last'],
                    'saved_timestamp': ['last'], 'volume': ['sum']}
            mkt_data = mkt_data.groupby(mkt_data.index / MAJOR_TICK_SIZE).agg(agg_funcs)
            mkt_data.columns = mkt_data.columns.droplevel(1)
            self.compressed_summary_tickers[mkt_name] = self.compressed_summary_tickers[mkt_name].append(mkt_data, ignore_index=True)
            self.summary_tickers[mkt_name] = pd.DataFrame()


        ## RATE LIMITER ##

    def rate_limiter_reset(self):
        self.api_tick = datetime.datetime.now()

    def rate_limiter_check(self):
        current_tick = datetime.datetime.now()
        return (current_tick - self.api_tick) < self.rate_limit

    def rate_limiter_limit(self):
        if BACKTESTING != 'TRUE':
            current_tick = datetime.datetime.now()
            if self.rate_limiter_check():
                sleep_for = self.rate_limit - (current_tick - self.api_tick)
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
        log.debug('{BOT} == GET market summaries ==')
        return self.btrx.getmarketsummaries()

    def get_market_history(self, market):
        log.debug('{BOT} == GET market history ==')
        return self.btrx.getmarkethistory(market)

    def get_order_book(self, market, order_type, depth):
        log.debug('{BOT} == GET order book ==')
        return self.btrx.getorderbook(market, order_type, depth)

    def get_ticker(self, market):
        log.debug('{BOT} == GET ticker ==')
        return self.btrx.getticker(market)

    def get_markets(self):
        log.debug('{BOT} == GET markets ==')
        return self.btrx.getmarkets(self.base_currencies)

    def get_currencies(self):
        log.debug('{BOT} == GET currencies ==')
        return self.btrx.getcurrencies()


        ## ORDERS ##

    def calculate_num_coins(self, market, order_type, quantity):
        """Calculates the QUANTITY for a trade
            -   if the order_type is 'buy', input parameter quantity is an amount of the base_currency to spend
            -   if the order_type is 'sell', inpute parameter quantity is a pct of the market_currency to sell

            an InsufficientFundsError will be raised in the event that there is not enough of the desired
            base currency for a 'buy' order
        """
        if order_type == 'buy':
            coin = market[:3]
            balance = self.get_balance(coin)
            rate = self.compressed_summary_tickers[market].loc[0, 'last']
            if balance['balance'] >= quantity:
                return round(quantity / rate, 8)
            else:
                msg = 'Not enough ' + coin + ' to complete this trade'
                raise InsufficientFundsError(balance, market, quantity, rate, msg)
        else:
            coin = market[4:]
            balance = self.get_balance(coin)
            return round(balance['balance'] * quantity, 8)

    def calculate_order_rate(self, market, order_type, quantity, order_book_depth=20):
        """Calculates the RATE for a trade

            gets the order_book for the desired market and adds up the available coins within
            the desired price range. the returned rate is the rate of the deepest level of the order book
            for the integrated quantity of open orders in the specified book.
        """
        if order_type == 'buy':
            book_type = 'sell'
        elif order_type == 'sell':
            book_type = 'buy'
        else:
            book_type = 'both'
        order_book = self.get_order_book(market, book_type, order_book_depth)
        current_total = 0
        rate = 0
        # calculate an instant price
        for order in order_book[book_type]:
            current_total += order['Quantity']
            rate = order['Rate']
            if current_total >= quantity:
                break
        return rate

    def buy_instant(self, market, quantity):
        log.debug('{BOT} == BUY instant ==')
        self.trade_instant('buy', market, quantity)

    def sell_instant(self, market, quantity):
        log.debug('{BOT} == SELL instant ==')
        self.trade_instant('sell', market, quantity)
        self.complete_sell(market)

    def trade_instant(self, order_type, market, quantity):
        try:
            num_coins = self.calculate_num_coins(market, order_type, quantity)
            rate = self.calculate_order_rate(market, order_type, num_coins, ORDER_BOOK_DEPTH)
            trade_resp = self.trade_functions[order_type](market, num_coins, rate)
            if trade_resp and not isinstance(trade_resp, basestring):
                self.trade_success(order_type, market, num_coins, rate, trade_resp['uuid'])
                return trade_resp
            else:
                log.info(trade_resp)
                return None
        except TradeFailureError:
            return None

    def trade_cancel(self, uuid):
        log.debug('{BOT} == CANCEL bid ==')
        try:
            trade_resp = self.btrx.cancel(uuid)
            self.psql.save_trade('CANCEL', 'market', 0, 0, trade_resp['uuid'])
            return trade_resp
        except Exception as e:
            log.error("*** !!! TRADE FAILED !!! ***")
            log.error(e)
            return None

    def trade_success(self, order_type, market, quantity, rate, uuid):
        timestamp = datetime.datetime.now()
        if os.getenv('BACKTESTING', 'FALSE') == 'TRUE':
            timestamp = self.btrx.current_timestamp
        trade_data = self.psql.save_trade(order_type, market, quantity, rate, uuid, timestamp)
        if market in self.completed_trades:
            self.completed_trades[market] = self.completed_trades[market].append(pd.Series(trade_data), ignore_index=True)
        else:
            self.completed_trades[market] = pd.DataFrame([trade_data])
        log.info('*** ' + order_type.upper() + ' Successful! ***')
        log.info("""
            market: """ + market + """
            quantity: """ + str(quantity) + """
            rate: """ + str(rate) + """
            trade id: """ + str(uuid))

    def should_buy(self, mkt_name):
        for strat in self.strats:
            if not strat.should_buy(mkt_name):
                return False
        return True

    def should_sell(self, mkt_name):
        for strat in self.strats:
            if not strat.should_sell(mkt_name):
                return False
        return True

    def execute_trades(self):
        for idx, market in self.markets.iterrows():
            mkt_name = market['marketname']
            if self.should_buy(mkt_name):
                self.buy_instant(mkt_name, MAX_CURRENCY_PER_BUY[mkt_name[:3]])
            elif self.should_sell(mkt_name) and self.can_sell(mkt_name):
                self.sell_instant(mkt_name, 1)

    def complete_sell(self, market):
        currencies = market.split('-')
        base_currency = currencies[0]
        market_currency = currencies[1]
        mkt_trade_data = self.completed_trades[market]
        tail = mkt_trade_data.tail(2).reset_index(drop=True)
        coin_in = tail.loc[0, 'quantity'] * tail.loc[0, 'rate']
        coin_out = tail.loc[1, 'quantity'] * tail.loc[1, 'rate']
        net_gain = coin_out - coin_in
        net_gain_pct = 100 * net_gain / coin_in
        hold_time = tail.loc[1, 'timestamp'] - tail.loc[0, 'timestamp']
        log_details = {
            'base_currency': base_currency,
            'market_currency': market_currency,
            'net_gain': net_gain,
            'net_gain_pct': net_gain_pct,
            'hold_time': hold_time}
        log.info(""""
            *** SELL details :\n\t
            Net Gain: {net_gain} {base_currency}, {net_gain_pct}%\n\t
            Hold Time: {hold_time}
            """.format(**log_details))
        if net_gain_pct <= -25:
            msg = """"{market_currency} Net Loss: {net_gain} {base_currency}, {net_gain_pct}%\n""".format(**log_details)
            # raise LargeLossError(log_details, msg)

            ## ACCOUNT ##

    def can_sell(self, mkt):
        balance = self.get_balance(mkt[4:])
        return balance['balance'] > 0

    def get_balances(self):
        log.debug('{BOT} == GET balances ==')
        balances = self.btrx.getbalances()
        return balances

    def get_balance(self, currency):
        log.debug('{BOT} == GET balance ==')
        balance = self.btrx.getbalance(currency)
        return balance

    def get_order_history(self, market, count):
        log.debug('{BOT} == GET order history ==')
        history = self.btrx.getorderhistory(market, count)
        return history


        ## BITTREX MARKET DATA COLLECTOR ##

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

    def collect_summaries(self):
        self.rate_limiter_reset()
        while True:
            try:
                self.increment_minor_tick()
                summaries = self.get_market_summaries()
                summaries = add_saved_timestamp(summaries, self.tick)
                self.psql.save_summaries(summaries)
                self.rate_limiter_limit()
            except Exception as e:
                log.error(e)
                self.reporter.send_report('Collect OrderBooks Failure', type(e).__name__ + ' :: ' + e.message)

    def collect_markets(self):
        markets = self.get_markets()
        self.psql.save_markets(markets)

    def collect_currencies(self):
        currencies = self.get_currencies()
        results = []
        for currency in currencies:
            currency_data = normalize_index(pd.Series(currency))
            results.append(currency_data)
        self.psql.save_currencies(results)

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
        self.plot_market_data()
        starting_balances = self.btrx.get_starting_balances()
        current_balances = self.btrx.getbalances()
        log.info('*** PERFORMANCE RESULTS ***')
        for currency in starting_balances:
            if currency not in self.tradeable_currencies and currency not in self.base_currencies:
                continue
            start = starting_balances[currency]['balance']
            end = current_balances[currency]['balance']
            log_statement = currency + ' :: ' + 'Start = ' + str(start) + ' , End = ' + str(end)
            if currency in self.base_currencies:
                log_statement += '% diff   :: ' + str((end - start) / start)
            log.info(log_statement)

    def cash_out(self):
        log.info('*** CASHING OUT ***')
        current_balances = self.btrx.getbalances()
        for idx, market in self.markets.iterrows():
            mkt_name = market['marketname']
            coins = mkt_name.split('-')
            cur_balance = current_balances[coins[1]]['balance']
            # add logic to optimize and get the best return (eth vs btc)
            if cur_balance > 0:
                self.trade_instant('sell', mkt_name, 1)

    def plot_market_data(self):
        for market, trades in self.completed_trades.iteritems():
            self.plotter.plot_market(market, self.compressed_summary_tickers[market], trades, self.strats)
