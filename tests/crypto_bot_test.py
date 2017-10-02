from src.bot.crypto_bot import CryptoBot
from src.strats.base_strat import BaseStrategy
from tests.mocks.btrx_mock import MockBittrex
from src.exceptions import LargeLossError
from fixtures.summary_tickers_fixture import SUMMARY_TICKERS_FIXTURE
from pandas.util.testing import assert_frame_equal
import pandas as pd
import os
import datetime
import pytest

os.environ['BACKTESTING'] = 'TRUE'
os.environ['BASE_CURRENCIES'] = 'BTC,ETH'
os.environ['COLLECT_FIXTURES'] = 'FALSE'

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

    def test_compress_and_calculate_mean(self):
        expected_result = pd.DataFrame([
            {'marketname': 'BTC-LTC', 'last': 0.015440, 'bid': 0.015450, 'ask': 0.015600,
             'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 0, 1)},
            {'marketname': 'BTC-LTC', 'last': 0.0154604, 'bid': 0.015451, 'ask': 0.015493,
             'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 5, 1)}
        ], columns=['ask', 'bid', 'last', 'marketname', 'saved_timestamp'])
        result = self.bot.compress_tickers({'BTC-LTC': SUMMARY_TICKERS_FIXTURE})
        assert_frame_equal(result['BTC-LTC'], expected_result, check_exact=False, check_less_precise=True)

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
        with pytest.raises(LargeLossError):
            self.bot.completed_trades = completed_trades
            self.bot.complete_sell(market)

    def test_calculate_order_rate(self):
        market = 'BTC-LTC'
        quantity = 5
        order_type = 'buy'
        order_rate = self.bot.calculate_order_rate(market, order_type, quantity)
        assert(order_rate == 0.06)
        order_type = 'sell'
        order_rate = self.bot.calculate_order_rate(market, order_type, quantity)
        assert(order_rate == 0.05)

    def test_calculate_num_coins(self):
        self.bot.minor_tick_step()
        market = 'BTC-LTC'
        order_type = 'buy'
        quantity = 0.1
        num_coins = self.bot.calculate_num_coins(market, order_type, quantity)
        assert(num_coins == 6.47668394)
        order_type = 'sell'
        quantity = 1
        num_coins = self.bot.calculate_num_coins(market, order_type, quantity)
        assert (num_coins == 20)
