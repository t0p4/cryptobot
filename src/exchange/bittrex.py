#!/usr/bin/env python
import hashlib
import hmac
import json
import time
import urllib
import urllib2
import pandas
import os
import pandas as pd

from src.utils.utils import normalize_index, normalize_columns


class Bittrex(object):
    
    def __init__(self):
        self.key = os.getenv('BITTREX_API_KEY', '')
        self.secret = os.getenv('BITTREX_API_SECRET', '')
        self.public = ['getmarkets', 'getcurrencies', 'getticker', 'getmarketsummaries', 'getmarketsummary', 'getorderbook', 'getmarkethistory']
        self.market = ['buylimit', 'buymarket', 'selllimit', 'sellmarket', 'cancel', 'getopenorders']
        self.account = ['getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorder', 'getorderhistory', 'getwithdrawalhistory', 'getdeposithistory']
        self.collect_fixtures = os.getenv('COLLECT_FIXTURES', 'FALSE')
        self.testing = os.getenv('TESTING', 'FALSE')

    def query(self, method, values={}):
        if method in self.public:
            url = 'https://bittrex.com/api/v1.1/public/'
        elif method in self.market:
            url = 'https://bittrex.com/api/v1.1/market/'
        elif method in self.account: 
            url = 'https://bittrex.com/api/v1.1/account/'
        else:
            return 'Something went wrong, sorry.'
        
        url += method + '?' + urllib.urlencode(values)
        
        if method not in self.public:
            url += '&apikey=' + self.key
            url += '&nonce=' + str(int(time.time()))
            signature = hmac.new(self.secret, url, hashlib.sha512).hexdigest()
            headers = {'apisign': signature}
        else:
            headers = {}
        
        req = urllib2.Request(url, headers=headers)
        response = json.loads(urllib2.urlopen(req).read())
        
        if response["result"]:
            return response["result"]
        else:
            return response["message"]

    def getmarkets(self):
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
            markets = pd.DataFrame(markets).drop(['created', 'issponsored', 'notice'], axis=1)
            return normalize_columns(markets)
    
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
            currencies = pd.DataFrame(currencies).drop(['notice'], axis=1)
            return normalize_columns(currencies)
    
    def getticker(self, market):
        return self.query('getticker', {'market': market})
    
    def getmarketsummaries(self):
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
        return self.query('buylimit', {'market': market, 'quantity': quantity, 'rate': rate})

    # DEPRECATED
    # def buymarket(self, market, quantity):
    #     return self.query('buymarket', {'market': market, 'quantity': quantity})

    def selllimit(self, market, quantity, rate):
        return self.query('selllimit', {'market': market, 'quantity': quantity, 'rate': rate})

    # DEPRECATED
    # def sellmarket(self, market, quantity):
    #     return self.query('sellmarket', {'market': market, 'quantity': quantity})
    
    def cancel(self, uuid):
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
    
    def getwithdrawalhistory(self, currency, count):
        return self.query('getwithdrawalhistory', {'currency': currency, 'count': count})
    
    def getdeposithistory(self, currency, count):
        return self.query('getdeposithistory', {'currency': currency, 'count': count})
