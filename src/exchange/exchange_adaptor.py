from src.exchange.binance.binance_api import BinanceAPI
from src.exchange.bittrex.bittrex_api import BittrexAPI
from src.exchange.backtest_exchange import BacktestExchange
from src.exchange.coinigy.coinigy_api import CoinigyAPI
from src.exchange.gemini.gemini_api import GeminiAPI
import pandas as pd
from src.utils.conversion_utils import convert_str_columns_to_num, get_usd_rate
from src.utils.utils import is_eth, is_btc
from src.exchange.gdax.gdax_api import PublicClient as GDaxPub
from datetime import datetime
from src.utils.logger import Logger
from src.utils.rate_limiter import RateLimiter
from src.exceptions import APIRequestError
from src.exchange.exchange_utils.binance_utils import create_normalized_trade_data_binance

log = Logger(__name__)

INTERVAL_RATES = {
    's': 1000,                      # second
    'm': 1000 * 60,                 # minute
    'h': 1000 * 60 * 60,            # hour
    'd': 1000 * 60 * 60 * 24,       # day
    'w': 1000 * 60 * 60 * 24 * 7    # week
}


class ExchangeAdaptor:
    def __init__(self, historical_rates):
        self.exchange_adaptors = {
            'binance': BinanceAPI,
            'bittrex': BittrexAPI,
            'coinigy': CoinigyAPI,
            'backtest': BacktestExchange,
            'gemini': GeminiAPI,
            'gdax_public': GDaxPub
        }
        self.rate_limiters = {
            'binance': RateLimiter('binance'),
            'bittrex': RateLimiter('bittrex'),
            'gdax_public': RateLimiter('gdax_public'),
            'gemini': RateLimiter('gemini')
        }
        self.exchange_pairs = {
            'binance': [],
            'bittrex': [],
            'gemini': []
        }
        self.historical_rates = historical_rates

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

    def check_rate_cache(self, timestamp, base_coin, mkt_coin):
        return self.historical_rates.get_rate(timestamp, base_coin, mkt_coin)

    #####################################################
    #                                                   #
    #   Formatting Utils                                #
    #                                                   #
    #####################################################

    @staticmethod
    def format_exchange_pair(exchange, mkt_coin, base_coin):
        if exchange == 'binance':
            return mkt_coin.upper() + base_coin.upper()
        elif exchange == 'gdax_public':
            return mkt_coin.upper() + '-' + base_coin.upper()

    @staticmethod
    def format_exchange_start_and_end_times(exchange, timestamp, minutes):
        divisor = 1
        if exchange == 'binance':
            divisor = 1
        elif exchange == 'gdax_public':
            divisor = 1000

        start = datetime.fromtimestamp(timestamp / divisor).isoformat()
        end = datetime.fromtimestamp(timestamp / divisor + (minutes * 60000 / divisor)).isoformat()
        return start, end

    @staticmethod
    def format_exchange_interval(exchange, interval):
        if exchange == 'binance':
            return interval
        elif exchange == 'gdax_public':
            return interval[0] * INTERVAL_RATES[interval[1]]
        elif exchange == 'gemini':
            return interval[0] * INTERVAL_RATES[interval[1]]

    #####################################################
    #                                                   #
    #   Instant USD Rates ::: TO DEPRECATE              #
    #                                                   #
    #####################################################

    def get_btc_usd_rate(self):
        ex = self.exchange_adaptors['gemini']()
        ticker = ex.pubticker('btcusd')
        return float(ticker['last'])

    def get_eth_usd_rate(self):
        ex = self.exchange_adaptors['gemini']()
        ticker = ex.pubticker('ethusd')
        return float(ticker['last'])

    #####################################################
    #                                                   #
    #   Level 1 Routes                                  #
    #                                                   #
    #####################################################

    def get_historical_rate(self, exchange, timestamp=None, base_coin='btc', mkt_coin='eth', interval='1m'):
        """
            gets the desired pair rate from the specified time period
        :param exchange: 'binance'
        :param base_coin: 'BTC'
        :param mkt_coin: 'USD'
        :param timestamp: <unix timestamp>
        :param interval: <num><unit> (1m, 2h, 7d)
        :return: 0.43553
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            exists_in_cache, usd_rate = self.check_rate_cache(timestamp, base_coin, mkt_coin)
            if exists_in_cache:
                return usd_rate
            else:
                start, end = self.format_exchange_start_and_end_times(exchange, timestamp, 1)
                interval = self.format_exchange_interval(exchange, interval)
                pair = self.format_exchange_pair(exchange, mkt_coin, base_coin)
                ex = self.exchange_adaptors[exchange]()
                self.rate_limiters[exchange].limit()
                pair_rate = ex.get_historical_rate(pair=pair, start=start, end=end, interval=interval)
                return pair_rate
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def get_historical_trades(self, exchange, pair=None, start_time=None, end_time=None):
        """
            gets all account trades on specified exchange pair between specified time period
        :param exchange:
        :param start_time:
        :param end_time:
        :param base_coin:
        :param mkt_coin:
        :return:
        """
        try:
            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            trade_data = ex.get_historical_trades(pair=pair)
            return trade_data
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def get_historical_tickers(self, exchange, start_time=None, end_time=None, interval='1m'):
        """
            gets the tickers for a given exchange over a given time period with a specified interval
        :param exchange:
        :param start_time:
        :param end_time:
        :return:
        """

    def get_account_balances(self, exchange, coin=None):
        """
            gets the current holdings on a given exchange, defaults to all coins, ability to specify a coin
        :param exchange:
        :param coin:
        :return:
        """
        try:
            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            pair_rate = ex.get_account_balances(coin=coin)
            return pair_rate
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def get_current_tickers(self, exchange):
        """
            gets the current tickers for all pairs on a given exchange
        :param exchange:
        :return:
        """

    def get_current_pair_ticker(self, exchange, base_coin='btc', mkt_coin=None):
        """
            gets the most recent ticker data for a specified pair on a given exchange
        :param exchange:
        :param base_coin:
        :param mkt_coin:
        :return:
        """

    def buy_limit(self, exchange, amount, base_coin='btc', mkt_coin=None):
        """
            buys the specified amount of the specified mkt_coin on a given exchange
        :param exchange:
        :param amount:
        :param base_coin:
        :param mkt_coin:
        :return:
        """

    def sell_limit(self, exchange, amount, base_coin='btc', mkt_coin=None):
        """
            sells the specified amount of the specified mkt_coin on a given exchange
        :param exchange:
        :param amount:
        :param base_coin:
        :param mkt_coin:
        :return:
        """

    def get_order_status(self, exchange, order_id=None, base_coin=None, mkt_coin=None):
        """
            gets the orders status of a specified order_id on a given exchange
        :param exchange:
        :param order_id:
        :param base_coin:
        :param mkt_coin:
        :return:
        """

    def get_order_book(self, exchange, base_coin='btc', mkt_coin=None, depth=None):
        """
            gets the order book to a given depth for a specified pair on a given exchange
        :param exchange:
        :param base_coin:
        :param mkt_coin:
        :param depth:
        :return:
        """

    def get_account_info(self, exchange):
        """
            returns the information for the account on the given exchange
        :param exchange:
        :return:
        """

    def initiate_withdrawal(self, exchange, coin, dest_addr):
        """
            initiates the withdrawal of a specified coin to a specified address from a given exchange
        :param exchange:
        :param coin:
        :param dest_addr:
        :return:
        """

    def get_exchange_pairs(self, exchange):
        """
            gets a list of the available pairs on a given exchange
        :param exchange: 'binance'
        :return: [{'pair': 'LTC-BTC', 'base_coin': 'BTC', 'mkt_coin': 'LTC'}, ...]
        """
        ex = self.exchange_adaptors[exchange]()
        self.exchange_pairs[exchange] = ex.get_exchange_pairs()
        return self.exchange_pairs[exchange]

    #####################################################
    #                                                   #
    #   Level 2 Routes                                  #
    #                                                   #
    #####################################################

    def get_all_historical_trade_data(self, exchange):
        """
            gets all of the trade data from a specified exchange and normalizes it
        :param exchange: 'binance'
        :return: {'LTC-BTC': <trade_data>, 'NEO-ETH': <trade_data>, ...}
        """
        try:
            pairs = self.get_exchange_pairs(exchange)
            trades_by_pair = {}
            for pair in pairs:
                log.info('getting historical trade data for {0} on {1}'.format(pair, exchange))
                ex = self.get_exchange_adaptor(exchange)
                trade_data = ex.get_historical_trades({'symbol': pair['pair']})
                trades_by_pair[pair['pair']] = self.normalize_trade_data(trade_data, pair, exchange=exchange)
            return trades_by_pair
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def get_historical_usd_vs_btc_eth_rates(self, timestamp):
        # TODO :: make exchange agnostic
        """
            queries gemini for the btc_usd and eth_usd rates at a given time
        :param timestamp: iso timestamp
        :return: {"ETH": 1050, "BTC": 11070}
        """
        # need to index into each of these variables, lists of lists
        # [0] gives the list of data requested, [4] is the 'close' price
        btc_usd = self.get_historical_rate(base_coin='USD', mkt_coin='BTC', timestamp=timestamp)
        eth_usd = self.get_historical_rate(base_coin='USD', mkt_coin='ETH', timestamp=timestamp)
        usd_market_rates = {'BTC': btc_usd, 'ETH': eth_usd}

        log.info("get_historical_usd_vs_btc_eth_rates :: " + repr(usd_market_rates))
        return usd_market_rates

    def get_historical_coin_vs_btc_eth_rates(self, timestamp, exchange, coin):
        """
            gets the coin rates on a given exchange at the specified timestamp
        :param timestamp: iso timestamp
        :param coin: LTC
        :return: {"ETH": 0.048, "BTC": 0.0094}
        """
        # TODO, handle pair not found error
        coin_btc_rate = self.get_historical_rate(base_coin='BTC', mkt_coin=coin, timestamp=timestamp, exchange=exchange)
        coin_eth_rate = self.get_historical_rate(base_coin='ETH', mkt_coin=coin, timestamp=timestamp, exchange=exchange)
        coin_mkt_rates = {'BTC': coin_btc_rate, 'ETH': coin_eth_rate}
        log.info("get_historical_coin_vs_btc_eth_rates :: " + repr(coin_mkt_rates))
        return coin_mkt_rates

    def normalize_trade_data(self, trade_data, pair_meta_data, exchange):
        if exchange == 'binance':
            return self.normalize_trade_data_binance(trade_data, pair_meta_data)

    #####################################################
    #                                                   #
    #   Trade Data Normalization                        #
    #                                                   #
    #####################################################

    def normalize_trade_data_binance(self, trade_data, pair_meta_data):
        # get raw trade data from binance and normalize to our db schema
        normalized_trade_data = []
        for trade in trade_data:
            if trade['isBuyer']:
                trade_dir = 'buy'
            else:
                trade_dir = 'sell'

            # get trade rate and usd rate based on gdax usd rates
            rates = {'btc': None, 'eth': None, 'usd': None}
            if is_btc(pair_meta_data['mkt_coin']):
                rates['btc'] = float(trade['price'])
                rates['usd'] = get_usd_rate({'BTC': rates['btc']}, self.get_historical_usd_vs_btc_eth_rates(trade['time']))
            elif is_eth(pair_meta_data['mkd_coin']):
                rates['eth'] = float(trade['price'])
                rates['usd'] = get_usd_rate({'ETH': rates['eth']}, self.get_historical_usd_vs_btc_eth_rates(trade['time']))

            normalized_trade_data.append(create_normalized_trade_data_binance(trade, pair_meta_data, trade_dir, rates))
        return normalized_trade_data

    # def add_rates_to_trades(self, trade_data):
        # 'base_currency': pair_meta_data['base_coin'],
        # 'market_currency': pair_meta_data['mkt_coin'],
        # 'rate_btc': rates['btc'],
        # 'rate_eth': rates['eth'],
        # 'rate_usd': rates['usd'],