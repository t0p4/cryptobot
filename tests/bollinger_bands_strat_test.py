from src.strats.bollinger_bands_strat import BollingerBandsStrat
import pandas as pd
from pandas.util.testing import assert_frame_equal
from fixtures.summary_tickers_fixture import SUMMARY_TICKERS_FIXTURE

options = {
    'active': True,
    'market_names': ['BTC-LTC'],
    'num_standard_devs': 2,
    'sma_window': 20,
    'sma_stat_key': 'close',
    'minor_tick': 1,
    'major_tick': 15,
    'testing': True
}


class TestBBStrat:
    def setup_class(self):
        self.strat = BollingerBandsStrat(options)

    def teardown_class(self):
        self.strat = None

    def test_compress_and_calculate_mean(self):
        expected_result = pd.DataFrame([
            {'ask': 0.015600, 'basevolume': 3102.100000, 'bid': 0.015450, 'high': 0.0175, 'last': 0.015440,
             'low': 0.015106, 'openbuyorders': 2050.0, 'opensellorders': 5750.0, 'volume': 191514.111111},
            {'ask': 0.015521, 'basevolume': 3117.045112, 'bid': 0.015466, 'high': 0.0175, 'last': 0.015483,
             'low': 0.015106, 'openbuyorders': 2150.133333, 'opensellorders': 5755.133333, 'volume': 192502.723944}
        ])
        result = self.strat.compress_and_calculate_mean(SUMMARY_TICKERS_FIXTURE)
        assert_frame_equal(result, expected_result, check_exact=False, check_less_precise=True)
