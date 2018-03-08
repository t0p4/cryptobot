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
        self.public = ['getmarkets', 'getcurrencies', 'getticker', 'getmarketsummaries', 'getmarketsummary', 'getorderbook', 'getmarkethistory']
        self.market = ['buylimit', 'buymarket', 'selllimit', 'sellmarket', 'cancel', 'getopenorders']
        self.account = ['getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorder', 'getorderhistory', 'getwithdrawalhistory', 'getdeposithistory']
        self.collect_fixtures = os.getenv('COLLECT_FIXTURES', 'FALSE')
        self.BACKTESTING = os.getenv('BACKTESTING', 'FALSE')
        self.PROD_TESTING = os.getenv('PROD_TESTING', 'TRUE')

    def query(self, method, values={}):
        if method in self.public:
            url = 'https://bittrex.com/api/v1.1/public/'
        elif method in self.market:
            url = 'https://bittrex.com/api/v1.1/market/'
        elif method in self.account: 
            url = 'https://bittrex.com/api/v1.1/account/'
        else:
            return 'Something went wrong, sorry.'
        
        url += method + '?' + urlencode(values)
        
        if method not in self.public:
            url += '&apikey=' + self.key
            url += '&nonce=' + str(int(time.time()))
            signature = hmac.new(self.secret.encode(), url.encode(), hashlib.sha512).hexdigest()
            headers = {'apisign': signature}
        else:
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

    def getallorderhistory(self, count):
        return self.query('getorderhistory', {'count': count})
    
    def getwithdrawalhistory(self, currency, count):
        return self.query('getwithdrawalhistory', {'currency': currency, 'count': count})
    
    def getdeposithistory(self, currency, count):
        return self.query('getdeposithistory', {'currency': currency, 'count': count})

        #####################################################
        #                                                   #
        #   CC Functions                                    #
        #                                                   #
        #####################################################

    def get_account_balances(self, coin=None):
        if coin is None:
            balances = self.getbalances()
            return [self.normalize_balance(balance) for balance in balances]
        else:
            balances = self.getbalance(coin)
            return self.normalize_balance(balances)

    @staticmethod
    def normalize_balance(balance):
        return {
            'coin': balance['Currency'],
            'balance': balance['Balance'],
            'address': balance['CryptoAddress']
        }

    def get_historical_rate(self, pair, timestamp=None, interval='1m'):
        raise APIDoesNotExistError('bittrex', 'get_historical_rate')

    def get_historical_trades(self, pair=None):
        # if pair is None:
        trades = self.getallorderhistory(500)
        # else:
        #     trades = self.getorderhistory(None, 500)

        if trades == '':
            return None
        elif pair is None:
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
            'quantity': trade['Quantity'],
            'rate': trade['Price'],
            'trade_id': trade['OrderUuid'],
            'exchange_id': 'bittrex',
            'trade_time': trade['TimeStamp'],
            'trade_direction': trade_dir,
            'cost_avg_btc': 0,
            'cost_avg_eth': 0,
            'cost_avg_usd': 0,
            'analyzed': False,
            'rate_btc': None,
            'rate_eth': None,
            'rate_usd': None,
            'commish': None,            ## TODO :: CALCULATE COMMISH
            'commish_asset': None
        }

    def get_historical_tickers(self, start_time=None, end_time=None, interval='1m'):
        raise APIDoesNotExistError('bittrex', 'get_historical_tickers')

    def get_current_tickers(self):
        raise APIDoesNotExistError('bittrex', 'get_current_tickers')

    def get_current_pair_ticker(self, pair=None):
        return self.normalize_ticker(self.getticker(pair['pair']), pair)

    @staticmethod
    def normalize_ticker(tick, pair):
        return {
            'bid': tick['Bid'],
            'ask': tick['Ask'],
            'last': tick['Last'],
            'vol_base': None,           ## TODO :: GET CURRENT VOLUME
            'vol_mkt': None,
            'timestamp': time.time(),
            **pair
        }

    def buy_limit(self, amount, base_coin='btc', mkt_coin=None):
        raise APIDoesNotExistError('bittrex', 'buy_limit')

    def sell_limit(self, amount, base_coin='btc', mkt_coin=None):
        raise APIDoesNotExistError('bittrex', 'sell_limit')

    def get_order_status(self, order_id=None, base_coin=None, mkt_coin=None):
        raise APIDoesNotExistError('bittrex', 'get_order_status')

    def get_order_book(self, base_coin='btc', mkt_coin=None, depth=None):
        raise APIDoesNotExistError('bittrex', 'get_order_book')

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