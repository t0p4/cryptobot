from src.bot.crypto_bot import CryptoBot
from src.strats.base_strat import BaseStrategy
from tests.mocks.btrx_mock import MockBittrex
import pandas as pd
import os

os.environ['BACKTESTING'] = 'True'

strat_options = {
    'active': False,
    'market_names': [],
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
        expected_columns = ['marketname', 'volume', 'last', 'basevolume', 'bid', 'ask', 'openbuyorders', 'opensellorders']
        market_summaries = self.bot.get_market_summaries()
        assert(isinstance(market_summaries, list))
        for summary in market_summaries:
            assert(isinstance(summary, pd.Series))
            assert(len(summary.index) == len(expected_columns))
            for key in summary.index:
                assert(key in expected_columns)

    def test_tick_step(self):
        strat = BaseStrategy(strat_options)
        exchange = MockBittrex()
        self.bot = CryptoBot(strat, exchange)
        for i in range(0, 100):
            self.bot.tick_step()