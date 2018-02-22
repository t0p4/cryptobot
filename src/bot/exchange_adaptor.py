from src.exchange.binance.client import Client
from src.exchange.bittrex import Bittrex
from src.exchange.backtest_exchange import BacktestExchange
from src.exchange.coinigy.coinigy_api_rest import CoinigyREST
from src.exchange.gemini import Geminipy
import pandas as pd
from src.utils.conversion_utils import convert_str_columns_to_num, get_usd_rate
from src.utils.utils import is_eth, is_btc
import time
from src.exchange.gdax.public_client import PublicClient as GDaxPub
from datetime import datetime
from src.utils.logger import Logger
from src.utils.rate_limiter import RateLimiter

log = Logger(__name__)


class ExchangeAdaptor:
    def __init__(self):
        self.exchange_adaptors = {
            'binance': Client,
            'bittrex': Bittrex,
            'coinigy': CoinigyREST,
            'backtest': BacktestExchange,
            'gemini': Geminipy,
            'gdax_public': GDaxPub
        }
        self.rate_limiters = {
            'binance': RateLimiter('binance'),
            'gdax_public': RateLimiter('gdax_public')
        }
        self.exchange_pairs = {
            'binance': [],
            'bittrex': [],
            'gemini': []
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

    @staticmethod
    def format_exchange_pair(mkt_coin, base_coin, exchange):
        if exchange == 'binance':
            return mkt_coin.upper() + base_coin.upper()
        elif exchange == 'gdax_public':
            return mkt_coin.upper() + '-' + base_coin.upper()

    @staticmethod
    def format_exchange_start_and_end_times(timestamp, minutes, exchange):
        divisor = 1
        if exchange == 'binance':
            divisor = 1
        elif exchange == 'gdax_public':
            divisor = 1000

        start = datetime.fromtimestamp(timestamp / divisor).isoformat()
        end = datetime.fromtimestamp(timestamp / divisor + (minutes * 60000 / divisor)).isoformat()
        return start, end

    def get_btc_usd_rate(self):
        ex = self.exchange_adaptors['gemini']()
        ticker = ex.pubticker('btcusd')
        return float(ticker['last'])

    def get_eth_usd_rate(self):
        ex = self.exchange_adaptors['gemini']()
        ticker = ex.pubticker('ethusd')
        return float(ticker['last'])

    def get_historical_usd_rate(self, coin='btc', timestamp=datetime.now(), interval=300, exchange='gdax_public'):
        start, end = self.format_exchange_start_and_end_times(timestamp, 1, exchange)
        ex = self.exchange_adaptors[exchange]()
        pair = self.format_exchange_pair(coin, 'usd', exchange)
        self.rate_limiters[exchange].limit()
        # TODO extend for other exchanges, this function is for gdax specificially
        usd_rate = ex.get_product_historic_rate_close(pair, start=start, end=end, granularity=interval)
        return usd_rate

    def get_historical_exchange_rate(self, mkt_coin, timestamp=datetime.now(), base_coin='btc', interval=300, exchange='binance'):
        start, end = self.format_exchange_start_and_end_times(timestamp, 60, exchange)
        ex = self.exchange_adaptors[exchange]()
        pair = self.format_exchange_pair(mkt_coin, base_coin, exchange)
        self.rate_limiters[exchange].limit()
        # TODO extend for other exchanges, this function is for binance specificially
        pair_rate = ex.get_klines(symbol=pair, limit=1, interval='1m', startTime=start, endTime=end)
        return pair_rate

    def get_historical_trade_data(self, exchange):
        # binance
        ex = self.exchange_adaptors[exchange]()
        pairs = self.get_exchange_pairs(exchange)
        orders = {}
        for pair in pairs:
            log.info('getting historical trade data for ' + pair['symbol'] + ' on ' + exchange)
            trade_data = ex.get_my_trades(symbol=pair['symbol'])
            orders[pair['symbol']] = self.normalize_trade_data(trade_data, pair, exchange=exchange)
        # coinigy
        # ex = self.exchange_adaptors['coinigy']()
        # order_data = ex.orders()
        return orders

    def get_historical_usd_vs_btc_eth_rates(self, timestamp):
        """
            queries gemini for the btc_usd and eth_usd rates at a given time
        :param timestamp: iso timestamp
        :return: {"ETH": 1050, "BTC": 11070}
        """
        # need to index into each of these variables, lists of lists
        # [0] gives the list of data requested, [4] is the 'close' price
        btc_usd = self.get_historical_usd_rate(timestamp=timestamp, coin='BTC')
        eth_usd = self.get_historical_usd_rate(timestamp=timestamp, coin='ETH')
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
        coin_btc_rate = self.get_historical_exchange_rate(mkt_coin=coin, timestamp=timestamp, base_coin='btc', exchange=exchange)
        coin_eth_rate = self.get_historical_exchange_rate(mkt_coin=coin, timestamp=timestamp, base_coin='eth', exchange=exchange)
        coin_mkt_rates = {'BTC': coin_btc_rate, 'ETH': coin_eth_rate}
        log.info("get_historical_coin_vs_btc_eth_rates :: " + repr(coin_mkt_rates))
        return coin_mkt_rates

    def get_exchange_pairs(self, exchange):
        ex = self.exchange_adaptors[exchange]()
        exchange_info = ex.get_exchange_info()
        if exchange == 'binance':
            self.exchange_pairs[exchange] = [{'symbol': ex['symbol'], 'baseAsset': ex['baseAsset'], 'quoteAsset': ex['quoteAsset']} for ex in exchange_info['symbols']]
        return self.exchange_pairs[exchange]

    def normalize_trade_data(self, trade_data, pair_meta_data, exchange):
        if exchange == 'binance':
            return self.normalize_trade_data_binance(trade_data, pair_meta_data)

    def normalize_trade_data_binance(self, trade_data, pair_meta_data):
        ## get raw trade data from binance and normalize to our db schema
        normalized_trade_data = []
        for trade in trade_data:
            if trade['isBuyer']:
                trade_direction = 'buy'
            else:
                trade_direction = 'sell'

            # get trade rate and usd rate based on gdax usd rates
            rate_btc = None
            rate_eth = None
            rate_usd = None
            if is_btc(pair_meta_data['quoteAsset']):
                rate_btc = float(trade['price'])
                rate_usd = get_usd_rate({'BTC': rate_btc}, self.get_historical_usd_vs_btc_eth_rates(trade['time']))
            elif is_eth(pair_meta_data['quoteAsset']):
                rate_eth = float(trade['price'])
                rate_usd = get_usd_rate({'ETH': rate_eth}, self.get_historical_usd_vs_btc_eth_rates(trade['time']))

            normalized_trade_data.append({
                'order_type': 'limit',
                'base_currency': pair_meta_data['baseAsset'],
                'market_currency': pair_meta_data['quoteAsset'],
                'quantity': trade['qty'],
                'rate': trade['price'],
                'trade_id': trade['orderId'],
                'exchange_id': 'binance',
                'trade_time': trade['time'],
                'save_time': time.time(),
                'rate_btc': rate_btc,
                'rate_eth': rate_eth,
                'rate_usd': rate_usd,
                'trade_direction': trade_direction,
                'cost_avg_btc': 0,
                'cost_avg_eth': 0,
                'cost_avg_usd': 0,
                'analyzed': False
            })
        return normalized_trade_data
