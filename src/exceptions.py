class BotError(Exception):
    """Base Error class for CryptoBot errors"""
    def __init__(self, msg='Bot Error!'):
        super(BotError, self).__init__(msg)
    pass


class LargeLossError(BotError):
    """Raised when a large loss is realized after a SELL order is completed"""
    def __init__(self, error_details, msg=''):
        msg = 'Most recent sell caused a significant loss, something might be wrong...\n' + msg
        super(LargeLossError, self).__init__(msg)
        self.details = error_details
    pass


class TradeFailureError(BotError):
    """Raised when a trade fails"""
    def __init__(self, msg):
        super(TradeFailureError, self).__init__(msg)
    pass


class TradeWarning(BotError):
    """Raised when a trade is successful but something is amiss"""
    def __init__(self, msg):
        super(TradeWarning, self).__init__(msg)
    pass


class InsufficientFundsError(TradeFailureError, BotError):
    """Raise when a trade is attempted but there are not enough funds to execute it"""
    def __init__(self, balance, market, quantity, rate, msg):
        super(InsufficientFundsError, self).__init__(msg)
        self.market = market
        self.quantity = quantity
        self.balance = balance
    pass


class MixedTradeError(TradeWarning, BotError):
    """Raise when a sell is completed but the market currency was initially bought with a different base currency"""
    def __init__(self, buy_base_currency, sell_base_currency, market_currency, msg=''):
        msg = 'Bought ' + market_currency + ' with ' + buy_base_currency + ', sold to ' + sell_base_currency + '.  ' + msg
        super(MixedTradeError, self).__init__(msg)
        self.buy_base_currency = buy_base_currency
        self.sell_base_currency = sell_base_currency
        self.market_currency = market_currency
    pass


class MissingTickError(BotError):
    """Raise when in BACKTESTING mode but fixture data is missing a tick"""
    def __init__(self, missing_tick):
        msg = 'missing tick ' + str(missing_tick)
        super(MissingTickError, self).__init__(msg)
        self.missing_tick = missing_tick
    pass


class BadMathError(BotError):
    """Raise when something goes wrong because of bad math (ex. coin holdings go below 0 for a give coin)"""
    def __init__(self, func):
        msg = 'BAD MATH! func: ' + func
        super(BadMathError, self).__init__(msg)
        self.func = func
    pass


class InvalidCoinError(BotError):
    """Raise when something goes wrong because of a bad coin / coin that doesn't exist somewhere"""

    def __init__(self, coin):
        msg = 'BAD COIN! coin: ' + coin
        super(InvalidCoinError, self).__init__(msg)
        self.coin = coin

    pass


class APIRequestError(BotError):
    """Raise when something goes wrong inside an API route"""
    def __init__(self, api, fn, error_msg):
        super(APIRequestError, self).__init__(error_msg)
        self.api = api
        self.fn = fn
        self.error_msg = error_msg


class APIDoesNotExistError(BotError):
    """Raise when an function has not been filled in yet"""
    def __init__(self, from_class, from_function):
        super(APIDoesNotExistError, self).__init__(from_class + " :: " + from_function)
        self.from_class = from_class
        self.from_function = from_function
