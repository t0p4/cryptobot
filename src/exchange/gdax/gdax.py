#
# gdax/AuthenticatedClient.py
# Daniel Paquin
#
# For authenticated requests to the gdax exchange

import hmac
import hashlib
import time
import requests
import base64
import json
from requests.auth import AuthBase
from src.exchange.gdax.gdax_public import PublicClient
from src.exchange.gdax.gdax_auth import GdaxAuth
from src.exceptions import APIRequestError, APIDoesNotExistError, InvalidCoinError, InsufficientFundsError
import os
import datetime
import dateutil.parser as dp
from src.utils.rate_limiter import RateLimiter


GDAX_API_KEY = os.getenv('GDAX_API_KEY', '')
GDAX_API_SECRET = os.getenv('GDAX_API_SECRET', '')
GDAX_API_PASS = os.getenv('GDAX_API_PASS', '')


class GDAXAPI(PublicClient):
    def __init__(self, api_url="https://api.gdax.com", timeout=30):
        super(GDAXAPI, self).__init__(api_url)
        self.auth = GdaxAuth(GDAX_API_KEY, GDAX_API_SECRET, GDAX_API_PASS)
        self.timeout = timeout
        self.pairs = None
        self.rate_limiter = RateLimiter('gdax')

    def get_account(self, account_id):
        r = requests.get(self.url + '/accounts/' + account_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_accounts(self):
        return self.get_account('')

    def get_account_history(self, account_id):
        result = []
        r = requests.get(self.url + '/accounts/{}/ledger'.format(account_id), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if "cb-after" in r.headers:
            self.history_pagination(account_id, result, r.headers["cb-after"])
        return result

    def history_pagination(self, account_id, result, after):
        r = requests.get(self.url + '/accounts/{}/ledger?after={}'.format(account_id, str(after)), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if "cb-after" in r.headers:
            self.history_pagination(account_id, result, r.headers["cb-after"])
        return result

    def get_account_holds(self, account_id):
        result = []
        r = requests.get(self.url + '/accounts/{}/holds'.format(account_id), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if "cb-after" in r.headers:
            self.holds_pagination(account_id, result, r.headers["cb-after"])
        return result

    def holds_pagination(self, account_id, result, after):
        r = requests.get(self.url + '/accounts/{}/holds?after={}'.format(account_id, str(after)), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if "cb-after" in r.headers:
            self.holds_pagination(account_id, result, r.headers["cb-after"])
        return result

    def buy(self, **kwargs):
        kwargs["side"] = "buy"
        if "product_id" not in kwargs:
            kwargs["product_id"] = self.product_id
        r = requests.post(self.url + '/orders',
                          data=json.dumps(kwargs),
                          auth=self.auth,
                          timeout=self.timeout)
        return r.json()

    def sell(self, **kwargs):
        kwargs["side"] = "sell"
        r = requests.post(self.url + '/orders',
                          data=json.dumps(kwargs),
                          auth=self.auth,
                          timeout=self.timeout)
        return r.json()

    def cancel_order(self, order_id):
        r = requests.delete(self.url + '/orders/' + order_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def cancel_all(self, product_id=''):
        url = self.url + '/orders/'
        if product_id:
            url += "?product_id={}&".format(str(product_id))
        r = requests.delete(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_order(self, order_id):
        r = requests.get(self.url + '/orders/' + order_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_orders(self, product_id='', status=[]):
        result = []
        url = self.url + '/orders/'
        params = {}
        if product_id:
            params["product_id"] = product_id
        if status:
            params["status"] = status
        r = requests.get(url, auth=self.auth, params=params, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if 'cb-after' in r.headers:
            self.paginate_orders(product_id, status, result, r.headers['cb-after'])
        return result

    def paginate_orders(self, product_id, status, result, after):
        url = self.url + '/orders'

        params = {
            "after": str(after),
        }
        if product_id:
            params["product_id"] = product_id
        if status:
            params["status"] = status
        r = requests.get(url, auth=self.auth, params=params, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if 'cb-after' in r.headers:
            self.paginate_orders(product_id, status, result, r.headers['cb-after'])
        return result

    def get_fills(self, order_id='', product_id='', before='', after='', limit=''):
        result = []
        url = self.url + '/fills?'
        if order_id:
            url += "order_id={}&".format(str(order_id))
        if product_id:
            url += "product_id={}&".format(product_id)
        if before:
            url += "before={}&".format(str(before))
        if after:
            url += "after={}&".format(str(after))
        if limit:
            url += "limit={}&".format(str(limit))
        r = requests.get(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if 'cb-after' in r.headers and limit is not len(r.json()):
            return self.paginate_fills(result, r.headers['cb-after'], order_id=order_id, product_id=product_id)
        return result

    def paginate_fills(self, result, after, order_id='', product_id=''):
        url = self.url + '/fills?after={}&'.format(str(after))
        if order_id:
            url += "order_id={}&".format(str(order_id))
        if product_id:
            url += "product_id={}&".format(product_id)
        r = requests.get(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        if r.json():
            result.append(r.json())
        if 'cb-after' in r.headers:
            return self.paginate_fills(result, r.headers['cb-after'], order_id=order_id, product_id=product_id)
        return result

    def get_fundings(self, result='', status='', after=''):
        if not result:
            result = []
        url = self.url + '/funding?'
        if status:
            url += "status={}&".format(str(status))
        if after:
            url += 'after={}&'.format(str(after))
        r = requests.get(url, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        result.append(r.json())
        if 'cb-after' in r.headers:
            return self.get_fundings(result, status=status, after=r.headers['cb-after'])
        return result

    def repay_funding(self, amount='', currency=''):
        payload = {
            "amount": amount,
            "currency": currency  # example: USD
        }
        r = requests.post(self.url + "/funding/repay", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def margin_transfer(self, margin_profile_id="", transfer_type="", currency="", amount=""):
        payload = {
            "margin_profile_id": margin_profile_id,
            "type": transfer_type,
            "currency": currency,  # example: USD
            "amount": amount
        }
        r = requests.post(self.url + "/profiles/margin-transfer", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_position(self):
        r = requests.get(self.url + "/position", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def close_position(self, repay_only=""):
        payload = {
            "repay_only": repay_only or False
        }
        r = requests.post(self.url + "/position/close", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def deposit(self, amount="", currency="", payment_method_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "payment_method_id": payment_method_id
        }
        r = requests.post(self.url + "/deposits/payment-method", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def coinbase_deposit(self, amount="", currency="", coinbase_account_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "coinbase_account_id": coinbase_account_id
        }
        r = requests.post(self.url + "/deposits/coinbase-account", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def withdraw(self, amount="", currency="", payment_method_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "payment_method_id": payment_method_id
        }
        r = requests.post(self.url + "/withdrawals/payment-method", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def coinbase_withdraw(self, amount="", currency="", coinbase_account_id=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "coinbase_account_id": coinbase_account_id
        }
        r = requests.post(self.url + "/withdrawals/coinbase", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def crypto_withdraw(self, amount="", currency="", crypto_address=""):
        payload = {
            "amount": amount,
            "currency": currency,
            "crypto_address": crypto_address
        }
        r = requests.post(self.url + "/withdrawals/crypto", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_payment_methods(self):
        r = requests.get(self.url + "/payment-methods", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_coinbase_accounts(self):
        r = requests.get(self.url + "/coinbase-accounts", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def create_report(self, report_type="", start_date="", end_date="", product_id="", account_id="", report_format="",
                      email=""):
        payload = {
            "type": report_type,
            "start_date": start_date,
            "end_date": end_date,
            "product_id": product_id,
            "account_id": account_id,
            "format": report_format,
            "email": email
        }
        r = requests.post(self.url + "/reports", data=json.dumps(payload), auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_report(self, report_id=""):
        r = requests.get(self.url + "/reports/" + report_id, auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

    def get_trailing_volume(self):
        r = requests.get(self.url + "/users/self/trailing-volume", auth=self.auth, timeout=self.timeout)
        # r.raise_for_status()
        return r.json()

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
    # TODO
    def get_exchange_balances(self, coin=None):
        balances = self.get_accounts()
        if coin is None:
            return [self.normalize_balance(balance) for balance in balances]
        else:
            for balance in balances:
                if balance['currency'].lower() == coin.lower():
                    return self.normalize_balance(balance)
            raise InvalidCoinError(coin, 'gdax')

    @staticmethod
    def normalize_balance(balance):
        return {
            'coin': balance['currency'],
            'balance': float(balance['balance']),
            'address': None
        }

    #
    # GET HISTORICAL TRADES
    #
    # TODO
    # def get_historical_trades(self, pair=None):
    #     res = self._get_historical_trades(symbol=pair['pair'], limit_trades=500)
    #     res_json = res.json()
    #     if res.status_code != 200:
    #         self.throw_error('get_historical_trades', res_json)
    #     else:
    #         return [{**self.normalize_trade(trade), **pair} for trade in res_json]
    #
    # @staticmethod
    # def normalize_trade(trade):
    #     return {
    #         'order_type': 'limit',
    #         'quantity': float(trade['amount']),
    #         'rate': float(trade['price']),
    #         'trade_id': trade['tid'],
    #         'exchange_id': 'gemini',
    #         'trade_time': trade['timestampms'],
    #         'trade_direction': trade['type'],
    #         'cost_avg_btc': 0,
    #         'cost_avg_eth': 0,
    #         'cost_avg_usd': 0,
    #         'analyzed': False,
    #         'rate_btc': 0,
    #         'rate_eth': 0,
    #         'rate_usd': 0,
    #         'commish': 0,  ## TODO :: CALCULATE COMMISH
    #         'commish_asset': ''
    #     }

    #
    # GET TICKERS
    #
    # TODO
    def get_current_tickers(self):
        if self.pairs is None:
            self.pairs = self.get_exchange_pairs()
        pairs = []
        for p in self.pairs:
            self.rate_limiter.limit()
            pairs.append(self.get_current_pair_ticker(p))
        return pairs

    def get_current_pair_ticker(self, pair):
        try:
            res = self.get_product_ticker(pair['pair'])
            return self.normalize_ticker(res, pair)
        except Exception as e:
            print('ok')

    @staticmethod
    def normalize_ticker(tick, pair):
        return {
            'bid': float(tick['bid']),
            'ask': float(tick['ask']),
            'last': float(tick['price']),
            'vol_base': float(tick['volume']),
            'vol_mkt': float(tick['volume']) * float(tick['price']),
            'timestamp': dp.parse(tick['time']).strftime('%s'),
            'exchange': 'gdax',
            **pair
        }

    #
    # PLACE / CANCEL / STATUS ORDER
    #
    # TODO
    # def buy_limit(self, amount, price, pair):
    #     return self.order_limit(amount, price, 'buy', pair['pair'])
    #
    # def sell_limit(self, amount, price, pair):
    #     return self.order_limit(amount, price, 'sell', pair['pair'])
    #
    # def order_limit(self, amount, price, side, pair):
    #     res = self.new_order(self, amount, price, side, symbol=pair['pair'], type='exchange limit')
    #     res_json = res.json()
    #     if res.status_code != 200:
    #         self.throw_error('order_limit_' + side, res_json)
    #     else:
    #         return self.normalize_order_resp(res_json, pair)
    #
    # def cancel_order(self, order_id, pair):
    #     res = self._cancel_order(order_id)
    #     res_json = res.json()
    #     if res.status_code != 200:
    #         self.throw_error('cancel_order', res_json)
    #     else:
    #         return self.normalize_order_resp(res_json, pair)
    #
    # def get_order_status(self, order_id, pair):
    #     res = self.order_status(order_id)
    #     res_json = res.json()
    #     if res.status_code != 200:
    #         self.throw_error('get_order_status', res_json)
    #     else:
    #         return self.normalize_order_resp(res_json, pair)
    #
    # @staticmethod
    # def normalize_order_resp(order_resp, pair):
    #     return {
    #         'order_id': order_resp['order_id'],
    #         'exchange': 'gemini',
    #         'order_type': order_resp['type'],
    #         'pair': order_resp['symbol'],
    #         'base_coin': pair['base_coin'],
    #         'mkt_coin': pair['mkt_coin'],
    #         'side': order_resp['side'],
    #         'is_live': order_resp['is_live'],
    #         'is_cancelled': order_resp['is_cancelled'],
    #         'original_amount': float(order_resp['original_amount']),
    #         'executed_amount': float(order_resp['executed_amount']),
    #         'remaining_amount': float(order_resp['remaining_amount']),
    #         'price': float(order_resp['price']),
    #         'avg_price': float(order_resp['avg_execution_price']),
    #         'rate_btc': None,
    #         'rate_eth': None,
    #         'rate_usd': None,
    #         'cost_avg_btc': 0,
    #         'cost_avg_eth': 0,
    #         'cost_avg_usd': 0,
    #         'analyzed': False,
    #         'timestamp': order_resp['timestampms']
    #     }

    #
    # GET ORDER BOOK
    #
    # TODO
    # def get_order_book(self, pair, side):
    #     res = self.book(pair['pair'])
    #     res_json = res.json()
    #     if res.status_code != 200:
    #         self.throw_error('get_order_book', res_json)
    #     else:
    #         book = self.normalize_order_book(res_json)
    #         if side == 'both':
    #             return book
    #         else:
    #             return book[side]
    #
    # def normalize_order_book(self, order_book):
    #     return {
    #         'bids': [self.normalize_order(order) for order in order_book['bids']],
    #         'asks': [self.normalize_order(order) for order in order_book['asks']]
    #     }
    #
    # @staticmethod
    # def normalize_order(order):
    #     return {
    #         'price': float(order['price']),
    #         'amount': float(order['amount'])
    #     }

    #
    # GET EXCHANGE PAIRS
    #

    def get_exchange_pairs(self):
        res = self.get_products()
        return [self.normalize_exchange_pair(pair) for pair in res]

    @staticmethod
    def normalize_exchange_pair(pair):
        # can add BaseCurrencyLong and MarketCurrencyLong
        return {
            'pair': pair['id'],
            'base_coin': pair['quote_currency'],
            'mkt_coin': pair['base_currency']
        }

    def get_historical_rate(self, pair, start=None, end=None, interval=None):
        if pair is None or start is None or end is None:
            raise APIRequestError('gdax', 'get_historical_rate', "PAIR, START, and END required. pair: {0} start: {1}, end: {2}".format(pair, start, end))
        else:
            # TODO deal w/ empty response
            return self.get_product_historic_rates(product_id=pair, start=start, end=end, granularity=interval)[0][4]

    # TODO, get_historical_tickers, get_account_info, initiate_withdrawal

    # def get_historical_tickers(self, start_time=None, end_time=None, interval='1m'):
    #     raise APIDoesNotExistError('gemini', 'get_historical_tickers')
    #
    # def get_account_info(self):
    #     raise APIDoesNotExistError('gemini', 'get_account_info')
    #
    # def initiate_withdrawal(self, coin, dest_addr):
    #     raise APIDoesNotExistError('gemini', 'initiate_withdrawal')