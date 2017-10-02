from src.strats.bollinger_bands_strat import BollingerBandsStrat
import pandas as pd
from pandas.util.testing import assert_frame_equal, assert_series_equal
from fixtures.summary_tickers_fixture import SUMMARY_TICKERS_FIXTURE
from fixtures.processed_summary_tickers_fixture import PROCESSED_SUMMARY_TICKERS_FIXTURE
import os
import datetime

os.environ['BACKTESTING'] = 'True'

options = {
    'active': True,
    'market_names': ['BTC-LTC'],
    'num_standard_devs': 2,
    'sma_window': 5,
    'sma_stat_key': 'last',
    'minor_tick': 1,
    'major_tick': 5
}


class TestBBStrat:
    def setup_class(self):
        self.strat = BollingerBandsStrat(options)

    def teardown_class(self):
        self.strat = None

    def test_compress_and_calculate_mean(self):
        expected_result = pd.DataFrame([
            {'marketname': 'BTC-LTC', 'last': 0.015440, 'bid': 0.015450, 'ask': 0.015600,
             'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 0, 1)},
            {'marketname': 'BTC-LTC', 'last': 0.0154604, 'bid': 0.015451, 'ask': 0.015493,
             'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 5, 1)}
        ], columns=['ask', 'bid', 'last', 'marketname', 'saved_timestamp'])
        result = self.strat.compress_and_calculate_mean(SUMMARY_TICKERS_FIXTURE)
        assert_frame_equal(result, expected_result, check_exact=False, check_less_precise=True)

    def test_calc_bollinger_bands(self):
        result = self.strat.calc_bollinger_bands(PROCESSED_SUMMARY_TICKERS_FIXTURE)
        expected_result = pd.Series(
            {'ask': 2.2, 'bid': 2.2, 'last': 2.2, 'marketname': 'BTC-LTC',
             'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 20, 1), 'SMA': 2.0, 'STDDEV': 0.158114,
             'UPPER_BB': 2.316228, 'LOWER_BB': 1.683772},
            index=['ask', 'bid', 'last', 'marketname', 'saved_timestamp', 'SMA', 'STDDEV', 'UPPER_BB', 'LOWER_BB'],
            name=4
        )
        assert_series_equal(result.iloc[4], expected_result)
