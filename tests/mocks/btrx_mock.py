#!/usr/bin/env python
from tests.fixtures.market_summaries_fixture import MARKET_SUMMARIES_FIXTURE
from tests.fixtures.currencies_fixture import CURRENCIES_FIXTURE
from tests.fixtures.markets_fixture import MARKETS_FIXTURE

from src.exchange.bittrex import Bittrex


class MockBittrex(Bittrex):
    def __init__(self):
        Bittrex.__init__(self)
        self.results = {
            'getmarketsummaries': MARKET_SUMMARIES_FIXTURE,
            'getcurrencies': CURRENCIES_FIXTURE,
            'getmarkets': MARKETS_FIXTURE,
            'getbalances': []
        }
        self.collect_fixtures = 'FALSE'
        self.testing = 'TRUE'

    def query(self, method, values={}):
        if method in self.public:
            url = 'https://bittrex.com/api/v1.1/public/'
        elif method in self.market:
            url = 'https://bittrex.com/api/v1.1/market/'
        elif method in self.account:
            url = 'https://bittrex.com/api/v1.1/account/'
        else:
            return 'Something went wrong, sorry.'

        return self.results[method]
