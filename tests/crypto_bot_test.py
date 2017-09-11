from src.bot.crypto_bot import CryptoBot
from src.strats.base_strat import BaseStrategy
from tests.mocks.btrx_mock import MockBittrex
import pandas as pd
import os
import datetime

os.environ['BACKTESTING'] = 'True'

strat_options = {
    'active': False,
    'testing': True
}


class TestCryptoBot:
    def setup_class(self):
        strat = BaseStrategy(strat_options)
        exchange = MockBittrex()
        self.bot = CryptoBot(strat, exchange)

    def teardown_class(self):
        self.bot = None

    def test_get_market_summaries(self):
        expected_columns = ['marketname', 'volume', 'last', 'basevolume', 'bid', 'ask', 'openbuyorders',
                            'opensellorders']
        market_summaries = self.bot.get_market_summaries()
        assert (isinstance(market_summaries, list))
        for summary in market_summaries:
            assert (isinstance(summary, pd.Series))
            assert (len(summary.index) == len(expected_columns))
            for key in summary.index:
                assert (key in expected_columns)

    def test_complete_sell(self):
        market = 'BTC-LTC'
        completed_trades = {'BTC-LTC': pd.DataFrame([
            {'order_type': 'buy', 'market': 'BTC-LTC', 'quantity': 0.1, 'rate': 0.005, 'uuid': 'test1',
             'base_currency': 'BTC', 'market_currency': 'LTC', 'timestamp': datetime.datetime(2017, 1, 1, 1, 0)},
            {'order_type': 'buy', 'market': 'BTC-LTC', 'quantity': 0.1, 'rate': 0.006, 'uuid': 'test2',
             'base_currency': 'BTC', 'market_currency': 'LTC', 'timestamp': datetime.datetime(2017, 1, 1, 2, 30)},
            {'order_type': 'buy', 'market': 'BTC-LTC', 'quantity': 0.1, 'rate': 0.0065, 'uuid': 'test3',
             'base_currency': 'BTC', 'market_currency': 'LTC', 'timestamp': datetime.datetime(2017, 1, 1, 2, 45)},
            {'order_type': 'buy', 'market': 'BTC-LTC', 'quantity': 0.1, 'rate': 0.003, 'uuid': 'test4',
             'base_currency': 'BTC', 'market_currency': 'LTC', 'timestamp': datetime.datetime(2017, 1, 1, 4, 0)}
        ])}
        self.bot.completed_trades = completed_trades
        self.bot.complete_sell(market)
