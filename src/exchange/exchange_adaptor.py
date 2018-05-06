from src.exchange.binance.binance_api import BinanceAPI
from src.exchange.bittrex.bittrex_api import BittrexAPI
from src.exchange.backtest_exchange import BacktestExchange
from src.exchange.coinigy.coinigy_api import CoinigyAPI
from src.exchange.gemini.gemini_api import GeminiAPI
from src.exchange.cryptopia.cryptopia_api import CryptopiaAPI
from src.exchange.gdax.gdax import GDAXAPI
import pandas as pd
from src.utils.conversion_utils import convert_str_columns_to_num, get_usd_rate
from src.utils.utils import is_eth, is_btc
from src.exchange.gdax.gdax_public import PublicClient as GDaxPub
from datetime import datetime
from src.utils.logger import Logger
from src.utils.rate_limiter import RateLimiter
from src.exceptions import APIRequestError, InvalidCoinError
from src.exchange.exchange_utils.binance_utils import create_normalized_trade_data_binance
from src.data_structures.historical_prices import HistoricalRates

log = Logger(__name__)

INTERVAL_RATES = {
    's': 1000,  # second
    'm': 1000 * 60,  # minute
    'h': 1000 * 60 * 60,  # hour
    'd': 1000 * 60 * 60 * 24,  # day
    'w': 1000 * 60 * 60 * 24 * 7  # week
}


class ExchangeAdaptor:
    def __init__(self):
        self.exchange_adaptors = {
            'binance': BinanceAPI,
            'bittrex': BittrexAPI,
            'coinigy': CoinigyAPI,
            'backtest': BacktestExchange,
            'gemini': GeminiAPI,
            'gdax': GDAXAPI,
            'cryptopia': CryptopiaAPI
        }
        self.rate_limiters = {
            'binance': RateLimiter('binance'),
            'bittrex': RateLimiter('bittrex'),
            'gdax': RateLimiter('gdax'),
            'gemini': RateLimiter('gemini'),
            'cryptopia': RateLimiter('cryptopia')
        }
        self.exchange_pairs = {
            'binance': {},
            'bittrex': {},
            'gemini': {},
            'cryptopia': {}
        }
        self.balances = {
            'binance': {},
            'bittrex': {},
            'gemini': {},
            'cryptoptia': {}
        }
        self.exchange_divisors = {
            'binance': 1,
            'bittrex': 1,
            'gemini': 1000,
            'gdax': 1000,
            'cryptopia': 1
        }
        self.historical_rates = HistoricalRates('gemini')

    def get_exchange_adaptor(self, exchange):
        return self.exchange_adaptors[exchange]()

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
        elif exchange == 'bittrex':
            return base_coin.upper() + '-' + mkt_coin.upper()
        elif exchange == 'gemini':
            return mkt_coin.lower() + base_coin.lower()
        elif exchange == 'gdax':
            return mkt_coin.upper() + '-' + base_coin.upper()

    def format_exchange_start_and_end_times(self, exchange, timestamp, minutes):
        divisor = self.exchange_divisors[exchange]
        start = timestamp / divisor
        end = timestamp / divisor + (minutes * 60000 / divisor)
        if exchange == 'binance':
            return int(start), int(end)
        elif exchange == 'bittrex':
            return start, end
        elif exchange == 'gemini':
            return start, end
        elif exchange == 'gdax':
            return datetime.fromtimestamp(start).isoformat(), datetime.fromtimestamp(end).isoformat()
        elif exchange == 'cryptopia':
            return start, end

    @staticmethod
    def format_exchange_interval(exchange, interval):
        if exchange == 'binance':
            return interval
        elif exchange == 'bittrex':
            return interval
        elif exchange == 'gemini':
            return int(interval[0]) * INTERVAL_RATES[interval[1]]
        elif exchange == 'gdax':
            return int(int(interval[0]) * INTERVAL_RATES[interval[1]] / INTERVAL_RATES['s'])
        elif exchange == 'cryptopia':
            return interval

    @staticmethod
    def get_timestamp_delta(interval):
        return int(interval[0]) * INTERVAL_RATES[interval[1]]

    #####################################################
    #                                                   #
    #   Instant USD Rates ::: TO DEPRECATE              #
    #                                                   #
    #####################################################

    def get_btc_usd_rate(self):
        pair = {'pair': 'btcusd', 'base_coin': 'usd', 'mkt_coin': 'btc'}
        btc_usd_rate = self.get_current_pair_ticker(exchange='gemini', pair=pair)
        return float(btc_usd_rate['last'])

    def get_eth_usd_rate(self):
        pair = {'pair': 'btcusd', 'base_coin': 'usd', 'mkt_coin': 'btc'}
        eth_usd_rate = self.get_current_pair_ticker(exchange='gemini', pair=pair)
        return float(eth_usd_rate['last'])

    #####################################################
    #                                                   #
    #   Level 1 Routes                                  #
    #                                                   #
    #####################################################

    def add_pair_rate(self, timestamp, base_coin, rate_data):
        self.historical_rates.add_rate(timestamp, base_coin, rate_data)

    def get_historical_rate(self, exchange, timestamp=None, base_coin='BTC', mkt_coin='ETH', interval='1m'):
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
            # gemini has no historical rate endpoint
            if exchange == 'gemini':
                exchange = 'gdax'
            exists_in_cache, cache_rate = self.check_rate_cache(timestamp, base_coin, mkt_coin)
            if exists_in_cache:
                return cache_rate
            else:
                start, end = self.format_exchange_start_and_end_times(exchange, timestamp, 1)
                exchange_interval = self.format_exchange_interval(exchange, interval)
                pair = self.format_exchange_pair(exchange, mkt_coin, base_coin)
                ex = self.exchange_adaptors[exchange]()
                self.rate_limiters[exchange].limit()
                pair_rate = float(ex.get_historical_rate(pair=pair, start=start, end=end, interval=exchange_interval))
                return pair_rate
        except KeyError as e:
            log.error(e)
            new_timestamp = timestamp + self.get_timestamp_delta(interval)
            return self.get_historical_rate(exchange, timestamp=new_timestamp, base_coin=base_coin, mkt_coin=mkt_coin,
                                            interval=interval)
        except IndexError as e:
            log.error(e)
            new_timestamp = timestamp + self.get_timestamp_delta(interval)
            return self.get_historical_rate(exchange, timestamp=new_timestamp, base_coin=base_coin, mkt_coin=mkt_coin,
                                            interval=interval)
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def get_historical_trades(self, exchange, pair=None):
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
            if pair is None:
                raise APIRequestError(exchange, 'get_historical_trades', 'pair missing')
            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            trade_data = ex.get_historical_trades(pair=pair)
            if isinstance(trade_data, list):
                return trade_data
            else:
                raise APIRequestError(exchange, 'get_historical_trades', 'no trade data')
        except APIRequestError as e:
            log.error(e.error_msg)
            return []

    def get_historical_tickers(self, exchange, start_time=None, end_time=None, interval='1m'):
        """
            gets the tickers for a given exchange over a given time period with a specified interval
        :param exchange:
        :param start_time:
        :param end_time:
        :return:
        """

    def get_current_tickers(self, exchange, ohlc):
        """
            gets the current tickers for all pairs on a given exchange
        :param exchange:
        :return:
            [
                {   'pair': 'BTC-NEO',
                    'base_coin': 'BTC',
                    'mkt_coin': 'NEO',
                    'open': 0.0094,
                    'high': 0.0094,
                    'low': 0.0094,
                    'close': 0.0094,
                    'bid': 0.0092,
                    'ask': 0.0095,
                    'last': 0.0094,
                    'vol_base': 5,
                    'vol_mkt': 500,
                    'timestamp': 3847878274205,
                    'exchange': 'gemini'
                }
            ]
        """
        try:
            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            tickers = ex.get_current_tickers()
            result = []
            if ohlc:
                for ticker in tickers:
                    result.append({
                        **ticker,
                        'open': float(ticker['last']),
                        'high': float(ticker['last']),
                        'low': float(ticker['last']),
                        'close': float(ticker['last']),
                        'exchange': exchange
                    })
            else:
                result = tickers
            return result
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def get_current_pair_ticker(self, exchange, pair=None):
        """
            gets the most recent ticker data for a specified pair on a given exchange
        :param exchange:
        :param pair:
        :return:
            {
                'pair': 'BTC-NEO',
                'base_coin': 'BTC',
                'mkt_coin': 'NEO',
                'open': 0.0094,
                'high': 0.0094,
                'low': 0.0094,
                'close': 0.0094,
                'bid': 0.0092,
                'ask': 0.0095,
                'last': 0.0094,
                'vol_base': 5,
                'vol_mkt': 500,
                'timestamp': 3847878274205,
                'exchange': 'gemini'
            }
        """
        try:
            if pair is None:
                raise APIRequestError(exchange, 'get_current_pair_ticker', 'please specify a pair')
            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            ticker = ex.get_current_pair_ticker(pair)
            ticker = {
                **ticker,
                'open': float(ticker['last']),
                'high': float(ticker['last']),
                'low': float(ticker['last']),
                'close': float(ticker['last'])
            }
            return pd.DataFrame(ticker, index=[0])
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def buy_limit(self, exchange, amount=None, price=None, pair=None):
        """
            buys the specified amount of the specified mkt_coin on a given exchange
        :param exchange:
        :param amount:
        :param price:
        :param pair:
        :return:
            {
                "order_id": 382783,
                "pair": btcusd,
                "price": 0.425362,
                "avg_price": 0.452783,
                "side": <buy / sell>,
                "type": BUY_LIMIT,
                "timestampms": 12345678900909,
                "is_live": <true / false>,
                "is_cancelled": <true / false>,
                'executed_amount': 50,
                'remaining_amount': 20,
                'original_amount': 70,
                'exchange': 'gemini'
            }
        """

        try:
            if pair is None:
                raise APIRequestError(exchange, 'buy_limit', 'pair missing')
            if amount is None:
                raise APIRequestError(exchange, 'buy_limit', 'amount missing')
            if price is None:
                raise APIRequestError(exchange, 'buy_limit', 'price missing')
            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            return ex.buy_limit(amount, price, pair)
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def sell_limit(self, exchange, amount=None, price=None, pair=None):
        """
            sells the specified amount of the specified mkt_coin on a given exchange
        :param exchange:
        :param amount:
        :param price:
        :param pair:
        :return:
            {
                "order_id": 382783,
                "pair": btcusd,
                "price": 0.425362,
                "avg_price": 0.452783,
                "side": <buy / sell>,
                "type": BUY_LIMIT,
                "timestampms": 12345678900909,
                "is_live": <true / false>,
                "is_cancelled": <true / false>,
                'executed_amount': 50,
                'remaining_amount': 20,
                'original_amount': 70,
                'exchange': 'gemini'
            }
        """
        try:
            if pair is None:
                raise APIRequestError(exchange, 'sell_limit', 'pair missing')
            if amount is None:
                raise APIRequestError(exchange, 'sell_limit', 'amount missing')
            if price is None:
                raise APIRequestError(exchange, 'sell_limit', 'price missing')
            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            return ex.sell_limit(amount, price, pair)
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def cancel_order(self, exchange, order_id=None, pair=None):
        """
            cancels an existing order
        :param exchange:
        :param order_id:
        :param pair:
        :return:
            {
                "order_id": 382783,
                "pair": btcusd,
                "price": 0.425362,
                "avg_price": 0.452783,
                "side": <buy / sell>,
                "type": BUY_LIMIT,
                "timestampms": 12345678900909,
                "is_live": <true / false>,
                "is_cancelled": <true / false>,
                'executed_amount': 50,
                'remaining_amount': 20,
                'original_amount': 70,
                'exchange': 'gemini'
            }
        """

        try:
            if pair is None:
                raise APIRequestError(exchange, 'cancel_order', 'pair missing')
            if order_id is None:
                raise APIRequestError(exchange, 'cancel_order', 'order_id missing')
            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            return ex.cancel_order(order_id, pair)
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def get_order_status(self, exchange, order_id=None, pair=None):
        """
            gets the orders status of a specified order_id on a given exchange
        :param exchange:
        :param order_id:
        :param base_coin:
        :param mkt_coin:
        :return:
            {
                "order_id": 382783,
                "pair": "btcusd",
                "base_coin": "usd",
                "mkt_coin": "btc",
                "price": 0.425362,
                "avg_price": 0.452783,
                "side": <buy / sell>,
                "type": BUY_LIMIT,
                "timestampms": 12345678900909,
                "is_live": <true / false>,
                "is_cancelled": <true / false>,
                'executed_amount': 50,
                'remaining_amount': 20,
                'original_amount': 70,
                'exchange': 'gemini'
            }
        """
        try:
            if pair is None:
                raise APIRequestError(exchange, 'get_order_status', 'please specify a pair')
            if order_id is None:
                raise APIRequestError(exchange, 'get_order_status', 'please specify an order_id')

            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            order_status = ex.get_order_status(order_id, pair)
            return order_status
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def get_order_book(self, exchange, pair=None, side=None):
        """
            gets the order book to a given depth for a specified pair on a given exchange
        :param exchange:
        :param pair:
        :param side: <bids / asks>
        :return: {  'bids': [
                        {'price': <price>, 'amount': <amount>},
                        {...}
                    ],
                    'asks': [
                        {'price': <price>, 'amount': <amount>},
                        {...}
                    ],
                }
        """
        if side is None:
            side = 'both'
        try:
            if pair is None:
                raise APIRequestError(exchange, 'get_order_book', 'pair missing')

            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            order_book = ex.get_order_book(pair, side)
            return order_book
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

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
        :return: {'LTC-BTC': {'pair': 'LTC-BTC', 'base_coin': 'BTC', 'mkt_coin': 'LTC'}, ...}
        """
        ex = self.exchange_adaptors[exchange]()
        pair_list = ex.get_exchange_pairs()
        for pair in pair_list:
            self.exchange_pairs[exchange][pair['pair']] = pair
        return self.exchange_pairs[exchange]

    def get_current_timestamp(self, exchange):
        """
            need this to pull current timestamp when backtesting
            TODO: maybe deprecate
        :param exchange:
        :return:
        """
        return datetime.now()

    def get_coin_balance(self, exchange, coin):
        """
            returns the balance of the <coin> held on <exchange>
        :param exchange:
        :param coin:
        :return:
            {
                'coin': btc,
                'balance': 24.5,
                'address': 0xjklsdh82389hf98hf23hsdiufh
            }
        """
        try:
            if coin is None:
                raise APIRequestError(exchange, 'get_coin_balance', 'coin missing')
            if self.balances[exchange] is None or self.balances[exchange][coin] is None:
                self.get_exchange_balances(exchange)
            if coin in self.balances[exchange]:
                return self.balances[exchange][coin]
            else:
                raise InvalidCoinError(coin, exchange)
        except APIRequestError as e:
            log.error(e.error_msg)
            return None

    def get_exchange_balances(self, exchange):
        """
            returns and caches all non-zero balances held on <exchange>
        :param exchange:
        :return:
            [
                {
                    'coin': btc,
                    'balance': 24.5,
                    'address': 0xjklsdh82389hf98hf23hsdiufh
                },
                {
                    'coin': eth,
                    'balance': 68.3,
                    'address': 0xaywu7yw7y7yw8isq1200029shd
                }
            ]
        """
        try:
            ex = self.exchange_adaptors[exchange]()
            self.rate_limiters[exchange].limit()
            self.balances[exchange] = ex.get_exchange_balances()
            return self.balances[exchange]
        except APIRequestError as e:
            log.error(e.error_msg)
            return None
            # ex_adaptor = self.get_exchange_adaptor(exchange)
            # if exchange == 'binance':
            #     account = ex_adaptor.get_account({'recvWindow': 10000})
            #     result = []
            #     for balance in account['balances']:
            #         result.append({'currency': balance['asset'], 'balance': balance['free']})
            #     return pd.DataFrame(result)
            # elif exchange == 'coinigy':
            #     balances = ex_adaptor.balances()
            #     coinigy_col_keys = ['balance_amount_avail', 'balance_amount_held', 'balance_amount_total',
            #                         'btc_balance', 'last_price']
            #     return convert_str_columns_to_num(pd.DataFrame(balances), coinigy_col_keys)

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
            all_trades = []
            ex = self.get_exchange_adaptor(exchange)
            for sym, pair in pairs.items():
                log.info('getting historical trade data for {0} on {1}'.format(pair, exchange))
                self.rate_limiters[exchange].limit()
                trade_data = ex.get_historical_trades(pair)
                if trade_data is not None:
                    all_trades = all_trades + trade_data
            return all_trades
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
        btc_usd = self.get_historical_rate('gemini', base_coin='USD', mkt_coin='BTC', timestamp=timestamp)
        eth_usd = self.get_historical_rate('gemini', base_coin='USD', mkt_coin='ETH', timestamp=timestamp)
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

        coin_btc_rate = self.get_historical_rate_for_coin(base_coin='BTC', mkt_coin=coin, timestamp=timestamp,
                                                          exchange=exchange)
        if coin == 'BTC':
            coin_eth_rate = self.get_historical_rate_for_coin(base_coin=coin, mkt_coin='ETH', timestamp=timestamp,
                                                              exchange=exchange)
            coin_eth_rate = 1 / coin_eth_rate
        else:
            coin_eth_rate = self.get_historical_rate_for_coin(base_coin='ETH', mkt_coin=coin, timestamp=timestamp,
                                                            exchange=exchange)
        coin_mkt_rates = {'BTC': coin_btc_rate, 'ETH': coin_eth_rate}
        log.info("get_historical_coin_vs_btc_eth_rates :: " + repr(coin_mkt_rates))
        return coin_mkt_rates

    def get_historical_rate_for_coin(self, base_coin='', mkt_coin='', timestamp=0, exchange=''):
        # TODO, handle pair not found error
        coin_rate = 1
        if base_coin != mkt_coin:
            coin_rate = self.get_historical_rate(base_coin=base_coin, mkt_coin=mkt_coin, timestamp=timestamp,
                                                 exchange=exchange)
            log.info("get_historical rate_for _coin :: " + repr(coin_rate))
        return coin_rate

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
                rates['usd'] = get_usd_rate({'BTC': rates['btc']},
                                            self.get_historical_usd_vs_btc_eth_rates(trade['time']))
            elif is_eth(pair_meta_data['mkd_coin']):
                rates['eth'] = float(trade['price'])
                rates['usd'] = get_usd_rate({'ETH': rates['eth']},
                                            self.get_historical_usd_vs_btc_eth_rates(trade['time']))

            normalized_trade_data.append(create_normalized_trade_data_binance(trade, pair_meta_data, trade_dir, rates))
        return normalized_trade_data

        # def add_rates_to_trades(self, trade_data):
        # 'base_currency': pair_meta_data['base_coin'],
        # 'market_currency': pair_meta_data['mkt_coin'],
        # 'rate_btc': rates['btc'],
        # 'rate_eth': rates['eth'],
        # 'rate_usd': rates['usd'],
