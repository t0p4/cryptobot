#!/usr/bin/env python
import hashlib
import hmac
import json
import time
import requests
import os
import pandas as pd
import datetime
from src.utils.utils import normalize_index, normalize_columns
from src.exceptions import TradeFailureError, APIDoesNotExistError, APIRequestError
from src.utils.logger import Logger

log = Logger(__name__)


class BitfinexAPI(object):
    def __init__(self):
        self.key = os.getenv('BITFINEX_API_KEY', '')
        self.secret = str(os.getenv('BITFINEX_API_SECRET', ''))
        self.public = ['getmarkets', 'getcurrencies', 'getticker', 'getmarketsummaries', 'getmarketsummary', 'getorderbook', 'getmarkethistory']
        self.market = ['buylimit', 'buymarket', 'selllimit', 'sellmarket', 'cancel', 'getopenorders']
        self.account = ['getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorder', 'getorderhistory', 'getwithdrawalhistory', 'getdeposithistory']
        self.collect_fixtures = os.getenv('COLLECT_FIXTURES', 'FALSE')
        self.BACKTESTING = os.getenv('BACKTESTING', 'FALSE')
        self.PROD_TESTING = os.getenv('PROD_TESTING', 'TRUE')
        self.base_url = "https://api.bitfinex.com/v2"

    def get_historical_tickers(self, pair, start_time=0, end_time=0, interval='1h'):
        try:
            url = self.base_url + '/candles/trade:' + interval + ':tBTCUSD' + '/hist'
            data = {
                'limit': 1000000,
                'start': start_time,
                'end': end_time,
                'sort': 1
            }
            resp = requests.get(url, json.dumps(data))
            ticks = resp.json()

            if 'error' in ticks:
                log.warning('RATE LIMIT')
                time.sleep(60)

            res = []
            for tick in ticks:
                res.append(self.normalize_historical_tickers(pair, tick))
            return res
        except Exception as e:
            print(e)
            return None

    def normalize_historical_tickers(self, pair, tickers):
        'timestamp,open,high,low,close,volume_btc,volume_usd,weighted_price'
        return {
            'timestamp': tickers[0],
            'open': tickers[1],
            'high': tickers[3],
            'low': tickers[4],
            'close': tickers[2],
            'volume': tickers[5],
            'pair': pair['pair'],
            'base_coin': pair['base_coin'],
            'mkt_coin': pair['mkt_coin']
        }
