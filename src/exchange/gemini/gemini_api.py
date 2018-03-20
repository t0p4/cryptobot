"""
This module contains a class to make requests to the Gemini API.

Author: Mike Marzigliano
"""
import time
import json
import hmac
import base64
import hashlib
import requests
import os
from src.exceptions import InvalidCoinError, APIDoesNotExistError, APIRequestError


class GeminiAPI(object):
    """
    A class to make requests to the Gemini API.

    Make public or authenticated requests according to the API documentation:
    https://docs.gemini.com/
    """

    def __init__(self):
        """
        Initialize the class.

        Arguments:
        api_key -- your Gemini API key
        secret_key -- your Gemini API secret key for signatures
        live -- use the live API? otherwise, use the sandbox (default False)
        """
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.secret_key = os.getenv('GEMINI_API_SECRET', '')
        self.live_url = 'https://api.gemini.com'
        self.sandbox_url = 'https://api.sandbox.gemini.com'
        self.base_url = self.live_url

        self.pairs = None

    # public requests
    def symbols(self):
        """Send a request for all trading symbols, return the response."""
        url = self.base_url + '/v1/symbols'

        return requests.get(url)

    def pubticker(self, symbol='btcusd'):
        """Send a request for latest ticker info, return the response."""
        url = self.base_url + '/v1/pubticker/' + symbol

        return requests.get(url)

    def book(self, symbol='btcusd', limit_bids=0, limit_asks=0):
        """
        Send a request to get the public order book, return the response.

        Arguments:
        symbol -- currency symbol (default 'btcusd')
        limit_bids -- limit the number of bids returned (default 0)
        limit_asks -- limit the number of asks returned (default 0)
        """
        url = self.base_url + '/v1/book/' + symbol
        params = {
            'limit_bids': limit_bids,
            'limit_asks': limit_asks
        }

        return requests.get(url, params)

    def trades(self, symbol='btcusd', since=0, limit_trades=50,
               include_breaks=0):
        """
        Send a request to get all public trades, return the response.

        Arguments:
        symbol -- currency symbol (default 'btcusd')
        since -- only return trades after this unix timestamp (default 0)
        limit_trades -- maximum number of trades to return (default 50).
        include_breaks -- whether to display broken trades (default False)
        """
        url = self.base_url + '/v1/trades/' + symbol
        params = {
            'since': since,
            'limit_trades': limit_trades,
            'include_breaks': include_breaks
        }

        return requests.get(url, params)

    def auction(self, symbol='btcusd'):
        """Send a request for latest auction info, return the response."""
        url = self.base_url + '/v1/auction/' + symbol

        return requests.get(url)

    def auction_history(self, symbol='btcusd', since=0,
                        limit_auction_results=50, include_indicative=1):
        """
        Send a request for auction history info, return the response.

        Arguments:
        symbol -- currency symbol (default 'btcusd')
        since -- only return auction events after this timestamp (default 0)
        limit_auction_results -- maximum number of auction events to return
                                 (default 50).
        include_indicative -- whether to include publication of indicative
                              prices and quantities. (default True)
        """
        url = self.base_url + '/v1/auction/' + symbol + '/history'
        params = {
            'since': since,
            'limit_auction_results': limit_auction_results,
            'include_indicative': include_indicative
        }

        return requests.get(url, params)

    # authenticated requests
    def new_order(self, amount, price, side, client_order_id=None,
                  symbol='btcusd', type='exchange limit', options=None):
        """
        Send a request to place an order, return the response.

        Arguments:
        amount -- quoted decimal amount of BTC to purchase
        price -- quoted decimal amount of USD to spend per BTC
        side -- 'buy' or 'sell'
        client_order_id -- an optional client-specified order id (default None)
        symbol -- currency symbol (default 'btcusd')
        type -- the order type (default 'exchange limit')
        """
        request = '/v1/order/new'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce(),
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'side': side,
            'type': type
        }

        if client_order_id is not None:
            params['client_order_id'] = client_order_id

        if options is not None:
            params['options'] = options

        return requests.post(url, headers=self.prepare(params))

    def _cancel_order(self, order_id):
        """
        Send a request to cancel an order, return the response.

        Arguments:
        order_id - the order id to cancel
        """
        request = '/v1/order/cancel'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce(),
            'order_id': order_id
        }

        return requests.post(url, headers=self.prepare(params))

    def cancel_session(self):
        """Send a request to cancel all session orders, return the response."""
        request = '/v1/order/cancel/session'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce()
        }

        return requests.post(url, headers=self.prepare(params))

    def cancel_all(self):
        """Send a request to cancel all orders, return the response."""
        request = '/v1/order/cancel/all'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce()
        }

        return requests.post(url, headers=self.prepare(params))

    def order_status(self, order_id):
        """
        Send a request to get an order status, return the response.

        Arguments:
        order_id -- the order id to get information on
        """
        request = '/v1/order/status'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce(),
            'order_id': order_id
        }

        return requests.post(url, headers=self.prepare(params))

    def active_orders(self):
        """Send a request to get active orders, return the response."""
        request = '/v1/orders'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce()
        }

        return requests.post(url, headers=self.prepare(params))

    def _get_historical_trades(self, symbol='btcusd', limit_trades=50, timestamp=0):
        """
        Send a trade history request, return the response.

        Arguements:
        symbol -- currency symbol (default 'btcusd')
        limit_trades -- maximum number of trades to return (default 50)
        timestamp -- only return trades after this unix timestamp (default 0)
        """
        request = '/v1/mytrades'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce(),
            'symbol': symbol,
            'limit_trades': limit_trades,
            'timestamp': timestamp
        }

        return requests.post(url, headers=self.prepare(params))

    def tradevolume(self):
        """Send a request to get your trade volume, return the response."""
        request = '/v1/tradevolume'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce()
        }

        return requests.post(url, headers=self.prepare(params))

    def balances(self):
        """Send an account balance request, return the response."""
        request = '/v1/balances'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce()
        }

        return requests.post(url, headers=self.prepare(params))

    def newAddress(self, currency='btc', label=''):
        """
        Send a request for a new cryptocurrency deposit address
        with an optional label. Return the response.

        Arguements:
        currency -- a Gemini supported cryptocurrency (btc, eth)
        label -- optional label for the deposit address
        """
        request = '/v1/deposit/' + currency + '/newAddress'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce()
        }

        if label != '':
            params['label'] = label

        return requests.post(url, headers=self.prepare(params))

    def heartbeat(self):
        """Send a heartbeat message, return the response."""
        request = '/v1/heartbeat'
        url = self.base_url + request
        params = {
            'request': request,
            'nonce': self.get_nonce()
        }

        return requests.post(url, headers=self.prepare(params))

    def get_nonce(self):
        """Return the current millisecond timestamp as the nonce."""
        return int(round(time.time() * 1000))

    def prepare(self, params):
        """
        Prepare, return the required HTTP headers.

        Base 64 encode the parameters, sign it with the secret key,
        create the HTTP headers, return the whole payload.

        Arguments:
        params -- a dictionary of parameters
        """
        jsonparams = json.dumps(params)
        payload = base64.b64encode(jsonparams.encode())
        signature = hmac.new(self.secret_key.encode(), payload,
                             hashlib.sha384).hexdigest()

        return {'X-GEMINI-APIKEY': self.api_key,
                'X-GEMINI-PAYLOAD': payload,
                'X-GEMINI-SIGNATURE': signature}

    #####################################################
    #                                                   #
    #   CC Functions                                    #
    #                                                   #
    #####################################################

    @staticmethod
    def throw_error(fn, err):
        raise APIRequestError('gemini', fn, "gemini :: " + err['reason'] + " - " + err['message'])

    #
    # GET ACCOUNT BALANCES
    #

    def get_exchange_balances(self, coin=None):
        res = self.balances()
        res_json = res.json()
        if res.status_code != 200:
            self.throw_error('get_account_balances', res_json)
        else:
            if coin is None:
                return [self.normalize_balance(balance) for balance in res_json]
            else:
                for bal in res:
                    if bal['currency'].lower() == coin.lower():
                        return self.normalize_balance(bal)
                raise InvalidCoinError(coin, 'gemini')

    @staticmethod
    def normalize_balance(balance):
        return {
            'coin': balance['currency'],
            'balance': float(balance['amount']),
            'address': None
        }

    #
    # GET HISTORICAL TRADES
    #

    def get_historical_trades(self, pair=None):
        res = self._get_historical_trades(symbol=pair['pair'], limit_trades=500)
        res_json = res.json()
        if res.status_code != 200:
            self.throw_error('get_historical_trades', res_json)
        else:
            return [{**self.normalize_trade(trade), **pair} for trade in res_json]

    @staticmethod
    def normalize_trade(trade):
        return {
            'order_type': 'limit',
            'quantity': float(trade['amount']),
            'rate': float(trade['price']),
            'trade_id': trade['tid'],
            'exchange_id': 'gemini',
            'trade_time': trade['timestampms'],
            'trade_direction': trade['type'],
            'cost_avg_btc': 0,
            'cost_avg_eth': 0,
            'cost_avg_usd': 0,
            'analyzed': False,
            'rate_btc': None,
            'rate_eth': None,
            'rate_usd': None,
            'commish': None,  ## TODO :: CALCULATE COMMISH
            'commish_asset': None
        }

    #
    # GET TICKERS
    #

    def get_current_tickers(self):
        if self.pairs is None:
            self.pairs = self.get_exchange_pairs()
        pairs = []
        for p in self.pairs:
            pairs.append(self.get_current_pair_ticker(p))
        return pairs

    def get_current_pair_ticker(self, pair):
        res = self.pubticker(symbol=pair['pair'])
        res_json = res.json()
        if res.status_code != 200:
            self.throw_error('get_current_pair_ticker', res_json)
        else:
            return self.normalize_ticker(res_json, pair)

    @staticmethod
    def normalize_ticker(tick, pair):
        return {
            'bid': float(tick['bid']),
            'ask': float(tick['ask']),
            'last': float(tick['last']),
            'vol_base': float(tick['volume'][pair['base_coin'].upper()]),
            'vol_mkt': float(tick['volume'][pair['mkt_coin'].upper()]),
            'timestamp': tick['volume']['timestamp'],
            **pair
        }

    #
    # PLACE / CANCEL / STATUS ORDER
    #

    def buy_limit(self, amount, price, pair):
        return self.order_limit(amount, price, 'buy', pair['pair'])

    def sell_limit(self, amount, price, pair):
        return self.order_limit(amount, price, 'sell', pair['pair'])

    def order_limit(self, amount, price, side, pair):
        res = self.new_order(self, amount, price, side, symbol=pair['pair'], type='exchange limit')
        res_json = res.json()
        if res.status_code != 200:
            self.throw_error('order_limit_' + side, res_json)
        else:
            return self.normalize_order_resp(res_json, pair)

    def cancel_order(self, order_id, pair):
        res = self._cancel_order(order_id)
        res_json = res.json()
        if res.status_code != 200:
            self.throw_error('cancel_order', res_json)
        else:
            return self.normalize_order_resp(res_json, pair)

    def get_order_status(self, order_id, pair):
        res = self.order_status(order_id)
        res_json = res.json()
        if res.status_code != 200:
            self.throw_error('get_order_status', res_json)
        else:
            return self.normalize_order_resp(res_json, pair)

    @staticmethod
    def normalize_order_resp(order_resp, pair):
        return {
            'order_id': order_resp['order_id'],
            'exchange': 'gemini',
            'order_type': order_resp['type'],
            'pair': order_resp['symbol'],
            'base_coin': pair['base_coin'],
            'mkt_coin': pair['mkt_coin'],
            'side': order_resp['side'],
            'is_live': order_resp['is_live'],
            'is_cancelled': order_resp['is_cancelled'],
            'original_amount': float(order_resp['original_amount']),
            'executed_amount': float(order_resp['executed_amount']),
            'remaining_amount': float(order_resp['remaining_amount']),
            'price': float(order_resp['price']),
            'avg_price': float(order_resp['avg_execution_price']),
            'rate_btc': None,
            'rate_eth': None,
            'rate_usd': None,
            'cost_avg_btc': 0,
            'cost_avg_eth': 0,
            'cost_avg_usd': 0,
            'analyzed': False,
            'timestamp': order_resp['timestampms']
        }

    #
    # GET ORDER BOOK
    #

    def get_order_book(self, pair, side):
        res = self.book(pair['pair'])
        res_json = res.json()
        if res.status_code != 200:
            self.throw_error('get_order_book', res_json)
        else:
            book = self.normalize_order_book(res_json)
            if side == 'both':
                return book
            else:
                return book[side]

    def normalize_order_book(self, order_book):
        return {
            'bids': [self.normalize_order(order) for order in order_book['bids']],
            'asks': [self.normalize_order(order) for order in order_book['asks']]
        }

    @staticmethod
    def normalize_order(order):
        return {
            'price': float(order['price']),
            'amount': float(order['amount'])
        }

    #
    # GET EXCHANGE PAIRS
    #

    def get_exchange_pairs(self):
        res = self.symbols()
        res_json = res.json()
        if res.status_code != 200:
            self.throw_error('get_exchange_pairs', res_json)
        else:
            return [self.normalize_exchange_pair(sym) for sym in res_json]

    @staticmethod
    def normalize_exchange_pair(pair):
        # can add BaseCurrencyLong and MarketCurrencyLong
        return {
            'pair': pair,
            'base_coin': pair[3:],
            'mkt_coin': pair[:3]
        }

    # TODO, get_historical_rate, get_historical_tickers, get_account_info, initiate_withdrawal

    # def get_historical_rate(self, pair, timestamp=None, interval='1m'):
    #     raise APIDoesNotExistError('gemini', 'get_historical_rate')
    #
    # def get_historical_tickers(self, start_time=None, end_time=None, interval='1m'):
    #     raise APIDoesNotExistError('gemini', 'get_historical_tickers')
    #
    # def get_account_info(self):
    #     raise APIDoesNotExistError('gemini', 'get_account_info')
    #
    # def initiate_withdrawal(self, coin, dest_addr):
    #     raise APIDoesNotExistError('gemini', 'initiate_withdrawal')