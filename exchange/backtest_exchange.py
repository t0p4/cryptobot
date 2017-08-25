class BacktestExchange:
    def __init__(self, key1, key2):
        self.balances = {
            'USD': 20000,
            'BTC': 3
        }
        self.trades = {
            'USD': [],
            'BTC': []
        }

    def getmarkets(self):
        return [
            {
                "MarketCurrency": "USD",
                "BaseCurrency": "BTC",
                "MarketCurrencyLong": "Litecoin",
                "BaseCurrencyLong": "Bitcoin",
                "MinTradeSize": 0.01000000,
                "MarketName": "BTC-LTC",
                "IsActive": True,
                "Created": "2014-02-13T00:00:00"
            }
        ]

    def getcurrencies(self):
        return [
            {
                "Currency" : "BTC",
                "CurrencyLong" : "Bitcoin",
                "MinConfirmation" : 2,
                "TxFee" : 0.00020000,
                "IsActive" : True,
                "CoinType" : "BITCOIN",
                "BaseAddress" : ''
            }
        ]

    def getticker(self, market):
        return self.query('getticker', {'market': market})

    # def getmarketsummaries(self):
    #     pull market summaries from database

    # def getmarketsummary(self, market):
    #     return self.query('getmarketsummary', {'market': market})
    #
    # def getorderbook(self, market, type, depth=20):
    #     return self.query('getorderbook', {'market': market, 'type': type, 'depth': depth})
    #
    # def getmarkethistory(self, market, count=20):
    #     return self.query('getmarkethistory', {'market': market, 'count': count})
    #
    def buylimit(self, market, quantity, rate):
        trade = {'order_type': 'buy', 'market': market, 'quantity': quantity, 'rate': rate}
        return self.trades[market].append(trade)
    #
    # # DEPRECATED
    # # def buymarket(self, market, quantity):
    # #     return self.query('buymarket', {'market': market, 'quantity': quantity})
    #
    def selllimit(self, market, quantity, rate):
        trade = {'order_type': 'sell', 'market': market, 'quantity': quantity, 'rate': rate}
        return self.trades[market].tail
    #
    # # DEPRECATED
    # # def sellmarket(self, market, quantity):
    # #     return self.query('sellmarket', {'market': market, 'quantity': quantity})
    #
    # def cancel(self, uuid):
    #     return self.query('cancel', {'uuid': uuid})
    #
    # def getopenorders(self, market):
    #     return self.query('getopenorders', {'market': market})
    #
    # def getbalances(self):
    #     return self.query('getbalances')
    #
    # def getbalance(self, currency):
    #     return self.query('getbalance', {'currency': currency})
    #
    # def getdepositaddress(self, currency):
    #     return self.query('getdepositaddress', {'currency': currency})
    #
    # def withdraw(self, currency, quantity, address):
    #     return self.query('withdraw', {'currency': currency, 'quantity': quantity, 'address': address})
    #
    # def getorder(self, uuid):
    #     return self.query('getorder', {'uuid': uuid})
    #
    # def getorderhistory(self, market, count):
    #     return self.query('getorderhistory', {'market': market, 'count': count})
    #
    # def getwithdrawalhistory(self, currency, count):
    #     return self.query('getwithdrawalhistory', {'currency': currency, 'count': count})
    #
    # def getdeposithistory(self, currency, count):
    #     return self.query('getdeposithistory', {'currency': currency, 'count': count})