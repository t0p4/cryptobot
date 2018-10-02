#!/usr/bin/env python
import hashlib
import hmac
import json
import time
import urllib
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import pandas
import os
import pandas as pd
import datetime
from src.utils.utils import normalize_index, normalize_columns
from src.exceptions import TradeFailureError, APIDoesNotExistError, APIRequestError
from src.utils.logger import Logger

log = Logger(__name__)


class BittrexAPI(object):
    
    def __init__(self):
        self.key = os.getenv('BITTREX_API_KEY', '')
        self.secret = str(os.getenv('BITTREX_API_SECRET', ''))
        self.url = 'https://api.bitfinex.com/v2/'
        self.public = {
            'tickers': 'tickers?symbol=%s',
            'ticker': 'ticker/%s',
            'trades': 'trades/%s',
            'book': 'book/%s/%s',
            'stats1': 'stats',
            'candles': 'candles/trade:%s:%s/%s',
            'status': 'platform/status'
        }
        self.BACKTESTING = os.getenv('BACKTESTING', 'FALSE')
        self.PROD_TESTING = os.getenv('PROD_TESTING', 'TRUE')

    def query(self, method, values={}):
        url = self.url

        url += method + '?' + urlencode(values)
        
        # if method not in self.public:
        #     url += '&apikey=' + self.key
        #     url += '&nonce=' + str(int(time.time()))
        #     signature = hmac.new(self.secret.encode(), url.encode(), hashlib.sha512).hexdigest()
        #     headers = {'apisign': signature}
        # else:
        headers = {}
        
        req = Request(url, headers=headers)
        response = json.loads(urlopen(req).read())
        
        if response["result"]:
            return response["result"]
        else:
            return response["message"]

    def getmarkets(self, base_currencies):
        ## if collecting fixtures, return array of Series objects
        ## if running in production (or backtesting), return dataframe
        markets = self.query('getmarkets')
        if self.collect_fixtures == 'TRUE':
            results = []
            for market in markets:
                market_data = normalize_index(pd.Series(market))
                market_data.drop(['created', 'issponsored', 'notice'], inplace=True)
                results.append(market_data)
            return results
        else:
            markets = pd.DataFrame(markets).drop(['Created', 'IsSponsored', 'Notice'], axis=1)
            markets = markets[markets.apply((lambda mkt: mkt['MarketName'][:3] in base_currencies), axis=1)]
            return normalize_columns(markets)

    def getmarkets_v2(self):
        # v1 is from original bot
        markets = self.query('getmarkets')
        return markets
    
    def getcurrencies(self):
        currencies = self.query('getcurrencies')
        if self.collect_fixtures == 'TRUE':
            results = []
            for currency in currencies:
                currency_data = normalize_index(pd.Series(currency))
                currency_data.drop(['notice'], inplace=True)
                results.append(currency_data)
            return results
        else:
            currencies = pd.DataFrame(currencies)
            if 'notice' in currencies:
                currencies = currencies.drop(['notice'], axis=1)
            return normalize_columns(currencies)
    
    def getticker(self, market):
        return self.query('getticker', {'market': market})
    
    def getmarketsummaries(self):
        """Returns a <LIST> of <PANDAS.SERIES>"""
        summaries = self.query('getmarketsummaries')
        results = []
        for summary in summaries:
            summary_data = normalize_index(pandas.Series(summary))
            summary_data.drop(['timestamp', 'prevday', 'created', 'high', 'low'], inplace=True)
            results.append(summary_data)
        return results

    def get_market_summaries(self):
        return self.query('getmarketsummaries')
    
    def getmarketsummary(self, market):
        return self.query('getmarketsummary', {'market': market})
    
    def getorderbook(self, market, type, depth=20):
        return self.query('getorderbook', {'market': market, 'type': type, 'depth': depth})
    
    def getmarkethistory(self, market, count=20):
        return self.query('getmarkethistory', {'market': market, 'count': count})

    def buylimit(self, market, quantity, rate):
        if self.PROD_TESTING == 'TRUE':
            return {'uuid': hashlib.sha1(time.mktime(datetime.datetime.now().timetuple()))}
        else:
            try:
                return self.query('buylimit', {'market': market, 'quantity': quantity, 'rate': rate})
            except Exception as e:
                log.error(e)
                raise TradeFailureError

    # DEPRECATED
    # def buymarket(self, market, quantity):
    #     return self.query('buymarket', {'market': market, 'quantity': quantity})

    def selllimit(self, market, quantity, rate):
        if self.PROD_TESTING == 'TRUE':
            return {'uuid': hashlib.sha1(time.mktime(datetime.datetime.now().timetuple()))}
        else:
            try:
                return self.query('selllimit', {'market': market, 'quantity': quantity, 'rate': rate})
            except Exception as e:
                log.error("*** !!! TRADE FAILED !!! ***")
                raise TradeFailureError(e)

    # DEPRECATED
    # def sellmarket(self, market, quantity):
    #     return self.query('sellmarket', {'market': market, 'quantity': quantity})
    
    def cancel(self, uuid):
        if self.PROD_TESTING == 'TRUE':
            return {'uuid': hashlib.sha1(time.mktime(datetime.datetime.now().timetuple()))}
        else:
            return self.query('cancel', {'uuid': uuid})
    
    def getopenorders(self, market):
        return self.query('getopenorders', {'market': market})
    
    def getbalances(self):
        return self.query('getbalances')
    
    def getbalance(self, currency):
        return self.query('getbalance', {'currency': currency})
    
    def getdepositaddress(self, currency):
        return self.query('getdepositaddress', {'currency': currency})
    
    def withdraw(self, currency, quantity, address):
        return self.query('withdraw', {'currency': currency, 'quantity': quantity, 'address': address})
    
    def getorder(self, uuid):
        return self.query('getorder', {'uuid': uuid})
    
    def getorderhistory(self, market, count):
        return self.query('getorderhistory', {'market': market, 'count': count})

    def getallorderhistory(self):
        return self.query('getorderhistory', {})
    
    def getwithdrawalhistory(self, currency, count):
        return self.query('getwithdrawalhistory', {'currency': currency, 'count': count})
    
    def getdeposithistory(self, currency, count):
        return self.query('getdeposithistory', {'currency': currency, 'count': count})

        #####################################################
        #                                                   #
        #   CC Functions                                    #
        #                                                   #
        #####################################################

    def get_exchange_balances(self, coin=None):
        if coin is None:
            balances = self.getbalances()
            return [self.normalize_balance(balance) for balance in balances]
        else:
            balances = self.getbalance(coin)
            return self.normalize_balance(balances)

    @staticmethod
    def normalize_balance(balance):
        return {
            'exchange': 'bittrex',
            'coin': balance['Currency'],
            'balance': float(balance['Balance']),
            'address': balance['CryptoAddress']
        }

    def get_historical_rate(self, pair, timestamp=None, interval='1m'):
        raise APIDoesNotExistError('bittrex', 'get_historical_rate')

    def get_historical_trades(self, pair=None):
        # if pair is None:
        trades = self.getallorderhistory()
        # else:
        #     trades = self.getorderhistory(None, 500)

        if trades == '':
            return None
        elif pair is not None:
            return [{**self.normalize_trade(trade), **pair} for trade in trades]
        else:
            return self.normalize_trade(trades)

    @staticmethod
    def normalize_trade(trade):
        trade_dir = 'sell'
        if trade['OrderType'] == 'LIMIT_BUY':
            trade_dir = 'buy'

        return {
            'order_type': 'limit',
            'quantity': float(trade['Quantity']),
            'rate': float(trade['Price']),
            'trade_id': trade['OrderUuid'],
            'exchange_id': 'bittrex',
            'trade_time': trade['TimeStamp'],
            'trade_direction': trade_dir,
            'cost_avg_btc': 0,
            'cost_avg_eth': 0,
            'cost_avg_usd': 0,
            'analyzed': False,
            'rate_btc': 0,
            'rate_eth': 0,
            'rate_usd': 0,
            'commish': 0,            ## TODO :: CALCULATE COMMISH
            'commish_asset': 0
        }

    def get_historical_tickers(self, start_time=None, end_time=None, interval='1m'):
        raise APIDoesNotExistError('bittrex', 'get_historical_tickers')

    def get_current_tickers(self):
        tickers = self.get_market_summaries()
        return [self.normalize_ticker(tick, None) for tick in tickers]

    def get_current_pair_ticker(self, pair=None):
        return self.normalize_ticker(self.getticker(pair['pair']), pair)

    @staticmethod
    def normalize_ticker(tick, pair):
        if pair is not None:
            return {
                'bid': float(tick['Bid']),
                'ask': float(tick['Ask']),
                'last': float(tick['Last']),
                'vol_base': None,           ## TODO :: GET CURRENT VOLUME
                'vol_mkt': None,
                'timestamp': time.time(),
                'exchange': 'bittrex',
                **pair
            }
        else:
            return {
                'bid': float(tick['Bid']),
                'ask': float(tick['Ask']),
                'last': float(tick['Last']),
                'vol_base': None,           ## TODO :: GET CURRENT VOLUME
                'vol_mkt': None,
                'timestamp': time.time(),
                'exchange': 'bittrex',
                'pair': tick['MarketName'],
                'base_coin': tick['MarketName'].split('-')[0],
                'mkt_coin': tick['MarketName'].split('-')[1]
            }

    def buy_limit(self, amount, price, pair):
        return self.buylimit(pair['pair'], amount, price)

    def sell_limit(self, amount, price, pair):
        return self.selllimit(pair['pair'], amount, price)

    def cancel_order(self, order_id, pair):
        return self.normalize_cancel_order(self.cancel(order_id))

    @staticmethod
    def normalize_cancel_order(cancelled_order):
        return cancelled_order

    def get_order_status(self, order_id=None):
        return self.normalize_order_status(self.getorder(order_id).json())

    @staticmethod
    def normalize_order_status(order_status):
        return {
            'price': float(order_status['Price']),
            'side': order_status['Type'].split('_')[1],
            'is_live': order_status['IsOpen'],
            'is_cancelled': order_status['CancelInitiated'],
            'executed_amount': float(order_status['Quantity']) - float(order_status['QuantityRemaining']),
            'remaining_amount': float(order_status['QuantityRemaining']),
            'original_amount': float(order_status['Quantity']),
            'order_id': order_status['OrderUuid']
        }

    def get_order_book(self, pair, side=None):
        return self.normalize_order_book(self.getorderbook(pair['pair'], side).json())

    def normalize_order_book(self, order_book):
        return {
            'bids': [self.normalize_order(order) for order in order_book['bids']],
            'asks': [self.normalize_order(order) for order in order_book['asks']]
        }

    @staticmethod
    def normalize_order(order):
        return {
            'price': float(order['Rate']),
            'amount': float(order['Quantity'])
        }

    def get_account_info(self):
        raise APIDoesNotExistError('bittrex', 'get_account_info')

    def initiate_withdrawal(self, coin, dest_addr):
        raise APIDoesNotExistError('bittrex', 'initiate_withdrawal')

    def get_exchange_pairs(self):
        mkts = self.getmarkets_v2()
        return [self.normalize_exchange_pair(mkt) for mkt in mkts]

    @staticmethod
    def normalize_exchange_pair(pair):
        # can add BaseCurrencyLong and MarketCurrencyLong
        return {
            'pair': pair['MarketName'],
            'base_coin': pair['BaseCurrency'],
            'mkt_coin': pair['MarketCurrency']
        }