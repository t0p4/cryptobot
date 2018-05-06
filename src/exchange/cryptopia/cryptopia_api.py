""" This is a wrapper for Cryptopia.co.nz API """


import json
import time
import hmac
import hashlib
import base64
import requests
import os
from src.exceptions import APIRequestError, APIDoesNotExistError
import dateutil.parser as dp

# using requests.compat to wrap urlparse (python cross compatibility over 9000!!!)
from requests.compat import quote_plus


class CryptopiaAPI(object):
    """ Represents a wrapper for cryptopia API """

    def __init__(self):
        self.key = os.getenv('CRYPTOPIA_API_KEY', '')
        self.secret = os.getenv('CRYPTOPIA_API_SECRET', '')
        self.public = ['GetCurrencies', 'GetTradePairs', 'GetMarkets',
                       'GetMarket', 'GetMarketHistory', 'GetMarketOrders', 'GetMarketOrderGroups']
        self.private = ['GetBalance', 'GetDepositAddress', 'GetOpenOrders',
                        'GetTradeHistory', 'GetTransactions', 'SubmitTrade',
                        'CancelTrade', 'SubmitTip', 'SubmitWithdraw', 'SubmitTransfer']

    def api_query(self, feature_requested, get_parameters=None, post_parameters=None):
        """ Performs a generic api request """
        time.sleep(1)
        if feature_requested in self.private:
            url = "https://www.cryptopia.co.nz/Api/" + feature_requested
            post_data = json.dumps(post_parameters)
            headers = self.secure_headers(url=url, post_data=post_data)
            req = requests.post(url, data=post_data, headers=headers)
            if req.status_code != 200:
                try:
                    req.raise_for_status()
                except requests.exceptions.RequestException as ex:
                    return None, "Status Code : " + str(ex)
            req = req.json()
            if 'Success' in req and req['Success'] is True:
                result = req['Data']
                error = None
            else:
                result = None
                error = req['Error'] if 'Error' in req else 'Unknown Error'
            return (result, error)
        elif feature_requested in self.public:
            url = "https://www.cryptopia.co.nz/Api/" + feature_requested + "/" + \
                  ('/'.join(i for i in get_parameters.values()
                           ) if get_parameters is not None else "")
            req = requests.get(url, params=get_parameters)
            if req.status_code != 200:
                try:
                    req.raise_for_status()
                except requests.exceptions.RequestException as ex:
                    return None, "Status Code : " + str(ex)
            req = req.json()
            if 'Success' in req and req['Success'] is True:
                result = req['Data']
                error = None
            else:
                result = None
                error = req['Error'] if 'Error' in req else 'Unknown Error'
            return (result, error)
        else:
            return None, "Unknown feature"

    def get_currencies(self):
        """ Gets all the currencies """
        return self.api_query(feature_requested='GetCurrencies')

    def get_tradepairs(self):
        """ GEts all the trade pairs """
        return self.api_query(feature_requested='GetTradePairs')

    def get_markets(self):
        """ Gets data for all markets """
        return self.api_query(feature_requested='GetMarkets')

    def get_market(self, market):
        """ Gets market data """
        return self.api_query(feature_requested='GetMarket',
                              get_parameters={'market': market})

    def get_history(self, market):
        """ Gets the full order history for the market (all users) """
        return self.api_query(feature_requested='GetMarketHistory',
                              get_parameters={'market': market})

    def get_orders(self, market):
        """ Gets the user history for the specified market """
        return self.api_query(feature_requested='GetMarketOrders',
                              get_parameters={'market': market})

    def get_ordergroups(self, markets):
        """ Gets the order groups for the specified market """
        return self.api_query(feature_requested='GetMarketOrderGroups',
                              get_parameters={'markets': markets})

    def get_balance(self, currency):
        """ Gets the balance of the user in the specified currency """
        result, error = self.api_query(feature_requested='GetBalance',
                                       post_parameters={'Currency': currency})
        if error is None and currency != '':
                result = result[0]
        return result, error

    def get_openorders(self, market):
        """ Gets the open order for the user in the specified market """
        return self.api_query(feature_requested='GetOpenOrders',
                              post_parameters={'Market': market})

    def get_deposit_address(self, currency):
        """ Gets the deposit address for the specified currency """
        return self.api_query(feature_requested='GetDepositAddress',
                              post_parameters={'Currency': currency})

    def get_tradehistory(self, market):
        """ Gets the trade history for a market """
        return self.api_query(feature_requested='GetTradeHistory',
                              post_parameters={'Market': market})

    def get_transactions(self, transaction_type):
        """ Gets all transactions for a user """
        return self.api_query(feature_requested='GetTransactions',
                              post_parameters={'Type': transaction_type})

    def submit_trade(self, market, trade_type, rate, amount):
        """ Submits a trade """
        return self.api_query(feature_requested='SubmitTrade',
                              post_parameters={'Market': market,
                                               'Type': trade_type,
                                               'Rate': rate,
                                               'Amount': amount})

    def cancel_trade(self, trade_type, order_id, tradepair_id):
        """ Cancels an active trade """
        return self.api_query(feature_requested='CancelTrade',
                              post_parameters={'Type': trade_type,
                                               'OrderID': order_id,
                                               'TradePairID': tradepair_id})

    def submit_tip(self, currency, active_users, amount):
        """ Submits a tip """
        return self.api_query(feature_requested='SubmitTip',
                              post_parameters={'Currency': currency,
                                               'ActiveUsers': active_users,
                                               'Amount': amount})

    def submit_withdraw(self, currency, address, amount):
        """ Submits a withdraw request """
        return self.api_query(feature_requested='SubmitWithdraw',
                              post_parameters={'Currency': currency,
                                               'Address': address,
                                               'Amount': amount})

    def submit_transfer(self, currency, username, amount):
        """ Submits a transfer """
        return self.api_query(feature_requested='SubmitTransfer',
                              post_parameters={'Currency': currency,
                                               'Username': username,
                                               'Amount': amount})

    def secure_headers(self, url, post_data):
        """ Creates secure header for cryptopia private api. """
        nonce = str(time.time() )
        md5 = hashlib.md5()
        jsonparams = post_data.encode('utf-8')
        md5.update(jsonparams)
        rcb64 = base64.b64encode(md5.digest()).decode('utf-8')
        
        signature = self.key + "POST" + quote_plus(url).lower() + nonce + rcb64
        hmacsignature = base64.b64encode(hmac.new(base64.b64decode(self.secret),
                                                  signature.encode('utf-8'),
                                                  hashlib.sha256).digest())
        header_value = "amx " + self.key + ":" + hmacsignature.decode('utf-8') + ":" + nonce
        return {'Authorization': header_value, 'Content-Type': 'application/json; charset=utf-8'}

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
            if coin is None:
                balances, error = self.get_balance('')
                return [self.normalize_balance(balance) for balance in balances]
            else:
                balance = self.get_balance(coin)
                return self.normalize_balance(balance)
        except Exception as e:
            self.throw_error('get_exchange_balances', e.__str__())


    @staticmethod
    def normalize_balance(balance):
        return {
            'coin': balance['Symbol'],
            'balance': float(balance['Total']),
            'address': balance['Address']
        }

    #
    # GET HISTORICAL TRADES
    #

    def get_historical_trades(self, pair):
        try:
            trades = self.get_tradehistory(pair['pair'])
            return [{**self.normalize_trade(trade, pair['base_coin']), **pair} for trade in trades[0]]
        except Exception as e:
            self.throw_error('get_historical_trades', e.__str__())


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
            tickers = self.get_all_tickers()
            pairs = self.get_exchange_pairs()
            res = []
            for tick in tickers:
                # find the matching pair
                pair = None
                i = 0
                while pair is None:
                    if pairs[i]['pair'] == tick['symbol']:
                        pair = pairs[i]
                    i += 1
                res.append(self.normalize_ticker(tick, pair))
            return res
        except (BinanceAPIException, BinanceRequestException) as e:
            self.throw_error('get_current_pair_ticker', e.__str__())


    def get_current_pair_ticker(self, pair):
        try:
            return self.normalize_ticker(self.get_ticker(symbol=pair['pair']), pair)
        except (BinanceAPIException, BinanceRequestException) as e:
            self.throw_error('get_current_pair_ticker', e.__str__())


    @staticmethod
    def normalize_ticker(tick, pair):
        return {
            'pair': tick['symbol'],
            'last': float(tick['price']),
            'exchange': 'binance',
            **pair
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
            e_info = self.get_exchange_info()
            return [self.normalize_exchange_pair(pair) for pair in e_info['symbols']]
        except (BinanceAPIException, BinanceRequestException) as e:
            self.throw_error('get_exchange_pairs', e.__str__())


    @staticmethod
    def normalize_exchange_pair(pair):
        return {
            'pair': pair['symbol'],
            'base_coin': pair['quoteAsset'],
            'mkt_coin': pair['baseAsset']
        }


    # TODO, get_historical_rate, get_account_info, initiate_withdrawal, get_historical_tickers, get_current_tickers

    def get_historical_rate(self, pair=None, start=None, end=None, interval='1m'):
        # OpenTime, Open, High, Low, Close, Volume, CloseTime, QuoteAssVol, NumTrades, TakeBuyBaseAssVol, TakeBuyQuoteAssVol, Ignore
        klines = self.get_klines(symbol=pair, limit=1, startTime=start, interval=interval)
        return klines[0][4]

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