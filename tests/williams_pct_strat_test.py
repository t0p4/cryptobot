from src.strats.williams_pct_strat import WilliamsPctStrat
import pandas as pd
from pandas.util.testing import assert_frame_equal, assert_series_equal
from fixtures.summary_tickers_fixture import SUMMARY_TICKERS_FIXTURE
from fixtures.processed_summary_tickers_fixture import PROCESSED_SUMMARY_TICKERS_FIXTURE
import os
import datetime

os.environ['BACKTESTING'] = 'True'

w_pct_options = {
    'name': 'WilliamsPct',
    'active': True,
    'market_names': [],
    'plot_overlay': False,
    'stat_key': 'last',
    'wp_window': 5,
    'minor_tick': 1,
    'major_tick': 5
}


class TestBBStrat:
    def setup_class(self):
        self.strat = WilliamsPctStrat(w_pct_options)

    def teardown_class(self):
        self.strat = None

    def test_calculate_williams_pct(self):
        expected_wp = -0.0
        wp = self.strat.calculate_williams_pct(PROCESSED_SUMMARY_TICKERS_FIXTURE)
        assert(wp == expected_wp)
