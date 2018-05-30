#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Provide the GateIO class to abstract web interaction
'''

from src.exchange.gateio.HttpUtil import getSign, httpGet, httpPost
import os
from src.exceptions import APIRequestError, APIDoesNotExistError

class GateIOAPI:
    def __init__(self):
        self.__api_url = 'data.gateio.io'
        self.__trade_url = 'api.gateio.io'
        self.__apiKey = os.getenv('GATEIO_API_KEY')
        self.__secretKey = os.getenv('GATEIO_API_SECRET')

    ## General methods that query the exchange

    #所有交易对
    def pairs(self):
        URL = "/api2/1/pairs"
        params=''
        return httpGet(self.__api_url, URL, params)

    #市场订单参数
    def marketinfo(self):
        URL = "/api2/1/marketinfo"
        params=''
        return httpGet(self.__api_url, URL, params)

    #交易市场详细行情
    def marketlist(self):
        URL = "/api2/1/marketlist"
        params=''
        return httpGet(self.__api_url, URL, params)

    #所有交易行情
    def tickers(self):
        URL = "/api2/1/tickers"
        params=''
        return httpGet(self.__api_url, URL, params)

    # 所有交易对市场深度
    def orderBooks(self):
        URL = "/api2/1/orderBooks"
        param=''
        return httpGet(self.__api_url, URL, param)

    #单项交易行情
    def ticker(self, param):
        URL = "/api2/1/ticker"
        return httpGet(self.__api_url, URL, param)

    # 单项交易对市场深度
    def orderBook(self, param):
        URL = "/api2/1/orderBook"
        return httpGet(self.__api_url, URL, param)

    # 历史成交记录
    def tradeHistory(self, param):
        URL = "/api2/1/tradeHistory"
        return httpGet(self.__api_url, URL, param)

    ## Methods that make use of the users keys

    #获取帐号资金余额
    def balances(self):
        URL = "/api2/1/private/balances"
        param = {}
        return httpPost(self.__trade_url, URL, param, self.__apiKey, self.__secretKey)

    # 获取充值地址
    def depositAddres(self,param):
        URL = "/api2/1/private/depositAddress"
        params = {'currency':param}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    # 获取充值提现历史
    def depositsWithdrawals(self, start,end):
        URL = "/api2/1/private/depositsWithdrawals"
        params = {'start': start,'end':end}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    # 买入
    def buy(self, currencyPair,rate, amount):
        URL = "/api2/1/private/buy"
        params = {'currencyPair': currencyPair,'rate':rate, 'amount':amount}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    # 卖出
    def sell(self, currencyPair, rate, amount):
        URL = "/api2/1/private/sell"
        params = {'currencyPair': currencyPair, 'rate': rate, 'amount': amount}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    # 取消订单
    def cancelOrder(self, orderNumber, currencyPair):
        URL = "/api2/1/private/cancelOrder"
        params = {'orderNumber': orderNumber, 'currencyPair': currencyPair}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    # 取消所有订单
    def cancelAllOrders(self, type, currencyPair):
        URL = "/api2/1/private/cancelAllOrders"
        params = {'type': type, 'currencyPair': currencyPair}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    # 获取下单状态
    def getOrder(self, orderNumber, currencyPair):
        URL = "/api2/1/private/getOrder"
        params = {'orderNumber': orderNumber, 'currencyPair': currencyPair}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    # 获取我的当前挂单列表
    def openOrders(self):
        URL = "/api2/1/private/openOrders"
        params = {}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    # 获取我的24小时内成交记录
    def mytradeHistory(self, currencyPair, orderNumber):
        URL = "/api2/1/private/tradeHistory"
        params = {'currencyPair': currencyPair, 'orderNumber': orderNumber}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    # 提现
    def withdraw(self, currency, amount, address):
        URL = "/api2/1/private/withdraw"
        params = {'currency': currency, 'amount': amount,'address':address}
        return httpPost(self.__trade_url, URL, params, self.__apiKey, self.__secretKey)

    #####################################################
    #                                                   #
    #   CC Functions                                    #
    #                                                   #
    #####################################################

    @staticmethod
    def throw_error(fn, err):
        raise APIRequestError('binance', fn, err)

    #
    # GET ACCOUNT BALANCES
    #

    def get_exchange_balances(self, coin=None):
        try:
            balances = self.balances()
            if coin is None:
                return [self.normalize_balance(balance, koin) for balance, koin in balances.items()]
            else:
                return self.normalize_balance(balances[coin], coin)
        except Exception as e:
            self.throw_error('get_exchange_balances', e.__str__())


    @staticmethod
    def normalize_balance(balance, coin):
        return {
            'coin': coin,
            'balance': float(balance),
            'address': None
        }

    #
    # GET HISTORICAL TRADES
    #

    def get_historical_trades(self, pair):
        raise APIDoesNotExistError('GateIOAPI', 'get_historical_trades')
        # try:
            # trades = self.get_tradehistory(pair['pair'])
            # return [{**self.normalize_trade(trade, pair['base_coin']), **pair} for trade in trades[0]]
        # except Exception as e:
        #     self.throw_error('get_historical_trades', e.__str__())


    @staticmethod
    def normalize_trade(trade, commish_asset):
        trade_dir = 'sell'
        if trade['Type']:
            trade_dir = 'buy'

        return {
            'order_type': 'limit',
            'quantity': float(trade['Amount']),
            'rate': float(trade['Rate']),
            'trade_id': trade['TradeId'],
            'exchange_id': 'cryptopia',
            'trade_time': dp.parse(trade['TimeStamp']).strftime('%s'),
            'trade_direction': trade_dir,
            'cost_avg_btc': 0,
            'cost_avg_eth': 0,
            'cost_avg_usd': 0,
            'analyzed': False,
            'rate_btc': 0,
            'rate_eth': 0,
            'rate_usd': 0,
            'commish': float(trade['Fee']),
            'commish_asset': commish_asset
        }


    #
    # GET PAIR TICKER
    #

    def get_current_tickers(self):
        try:
            tickers = self.tickers()
            res = []
            for pair, tick in tickers.items():
                # find the matching pair
                res.append(self.normalize_ticker(tick, pair))
            return res
        except Exception as e:
            self.throw_error('get_current_pair_ticker', e.__str__())

    def get_current_pair_ticker(self, pair):
        try:
            return self.normalize_ticker(self.ticker(pair))
        except Exception as e:
            self.throw_error('get_current_pair_ticker', e.__str__())

    def normalize_ticker(self, tick, pair):
        return {
            'last': float(tick['last']),
            'exchange': 'gatio',
            **self.normalize_exchange_pair(pair)
        }


    #
    # PLACE ORDER
    #

    def buy_limit(self, amount, price, pair):
        try:
            return self.order_limit_buy(symbol=pair['pair'], quantity=amount, price=price)
        except (BinanceAPIException, BinanceRequestException) as e:
            self.throw_error('buy_limit', e.__str__())


    def sell_limit(self, amount, price, pair):
        try:
            return self.order_limit_sell(symbol=pair['pair'], quantity=amount, price=price)
        except (BinanceAPIException, BinanceRequestException) as e:
            self.throw_error('sell_limit', e.__str__())


    def normalize_order_resp(self, order_data):
        return {
            "order_id": order_data['orderId'],
            "pair": order_data['symbol'],
            "price": float(order_data['price']),
            "timestampms": order_data['transactTime'],
            "original_amount": float(order_data['origQty']),
            "executed_amount": float(order_data['executedQty']),
            "remaining_amount": float(order_data['origQty']) - float(order_data['executedQty']),
            "is_live": order_data['status'] in (self.ORDER_STATUS_NEW, self.ORDER_STATUS_PARTIALLY_FILLED),
            "is_cancelled": order_data['status'] in (self.ORDER_STATUS_CANCELED, self.ORDER_STATUS_PENDING_CANCEL),
            "order_type": order_data['type'],
            "side": order_data['side'].lower()
        }


    #
    # CANCEL ORDER
    #

    def cancel_order(self, order_id, pair):
        try:
            return self.normalize_cancel_order(self._cancel_order(symbol=order_id, orderId=pair['pair']))
        except (BinanceAPIException, BinanceRequestException) as e:
            self.throw_error('cancel_order', e.__str__())


    @staticmethod
    def normalize_cancel_order(cancelled_order):
        return {
            "pair": cancelled_order['symbol'],
            "orderId": cancelled_order['orderId']
        }


    #
    # GET ORDER STATUS
    #

    def get_order_status(self, order_id, pair):
        try:
            return self.normalize_order_status(self.get_order(symbol=pair['pair'], orderId=order_id))
        except (BinanceAPIException, BinanceRequestException) as e:
            self.throw_error('get_order_status', e.__str__())


    def normalize_order_status(self, order_status):
        return {
            "price": float(order_status['price']),
            "side": order_status['side'].upper(),
            "is_live": order_status['status'] in (self.ORDER_STATUS_NEW, self.ORDER_STATUS_PARTIALLY_FILLED),
            "is_cancelled": order_status['status'] == self.ORDER_STATUS_CANCELED,
            "executed_amount": float(order_status['executedQty']),
            "remaining_amount": float(order_status['origQty']) - float(order_status['executedQty']),
            "original_amount": float(order_status['origQty']),
            "order_id": order_status['orderId']
        }


    #
    # GET ORDER BOOK
    #

    def get_order_book(self, pair):
        try:
            return self._get_order_book(symbol=pair['pair'])
        except (BinanceAPIException, BinanceRequestException) as e:
            self.throw_error('get_order_book', e.__str__())


    def normalize_order_book(self, order_book):
        return {
            'bids': [self.normalize_order(order) for order in order_book['bids']],
            'asks': [self.normalize_order(order) for order in order_book['asks']]
        }


    @staticmethod
    def normalize_order(order):
        return {
            'price': float(order[0]),
            'amount': float(order[1])
        }


    #
    # GET EXCHANGE PAIRS
    #

    def get_exchange_pairs(self):
        try:
            ex_pairs = self.pairs()
            return [self.normalize_exchange_pair(pair) for pair in ex_pairs]
        except Exception as e:
            self.throw_error('get_exchange_pairs', e.__str__())


    @staticmethod
    def normalize_exchange_pair(pair):
        coins = pair.split('_')
        return {
            'pair': pair,
            'base_coin': coins[1],
            'mkt_coin': coins[0]
        }


    # TODO, get_historical_rate, get_account_info, initiate_withdrawal, get_historical_tickers, get_current_tickers

    def get_historical_rate(self, pair=None, start=None, end=None, interval='1m'):
        # # OpenTime, Open, High, Low, Close, Volume, CloseTime, QuoteAssVol, NumTrades, TakeBuyBaseAssVol, TakeBuyQuoteAssVol, Ignore
        # klines = self.get_history(pair, start)
        # return klines[0][4]
        raise APIRequestError('cryptopia', 'get_historical_rate', 'cryptopia doesnt go back very far')
        #
        # def get_account_info(self):
        #     raise APIDoesNotExistError('binance', 'get_account_info')
        #
        # def initiate_withdrawal(self, coin, dest_addr):
        #     raise APIDoesNotExistError('binance', 'initiate_withdrawal')
        #
        # def get_historical_tickers(self, start_time=None, end_time=None, interval='1m'):
        #     raise APIDoesNotExistError('binance', 'get_historical_tickers')
        #
        # def get_current_tickers(self):
        #     raise APIDoesNotExistError('binance', 'get_current_tickers')