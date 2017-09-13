class BotError(Exception):
    """Base Error class for CryptoBot errors"""
    def __init__(self, msg='Bot Error!'):
        super(BotError, self).__init__(msg)
    pass


class LargeLossError(BotError):
    """Raised when a large loss is realized after a SELL order is completed"""
    def __init__(self, msg=''):
        msg = 'Most recent sell caused a significant loss, something might be wrong...\n' + msg
        super(LargeLossError, self).__init__(msg)
    pass


class TradeFailureError(BotError):
    """Raised when a trade fails"""
    def __init__(self, msg, error_details):
        super(TradeFailureError, self).__init__(msg)
        self.details = error_details
    pass
