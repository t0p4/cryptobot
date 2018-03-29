import pandas as pd
from src.strats.base_strat import BaseStrategy
from src.utils.logger import Logger
from datetime import datetime
log = Logger(__name__)


class IndexStrat2(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.sma_window = options['sma_window']
        self.index_depth = options['index_depth']
        self.ema_stat_key = self.stat_key + self.ema_suffix
        self.pct_weight_key = self.stat_key + self.pct_weight_suffix
        self.positions = None
        self.add_columns = [self.ema_stat_key, self.pct_weight_key]

    def handle_data(self, full_mkt_data):
        if full_mkt_data.groupby('id').agg('count').loc['bitcoin', 'symbol'] >= self.sma_window:
            full_mkt_data = self.calc_index(full_mkt_data)
            tail = full_mkt_data.tail(2)

            # # SPIKE CHASER
            buy = tail['last'].values[1] >= tail['UPPER_BB'].values[1] and tail['last'].values[0] < tail['UPPER_BB'].values[0]
            sell = tail['last'].values[1] < tail['SMA'].values[1] and tail['last'].values[0] >= tail['SMA'].values[0]

            # # STANDARD
            # buy = tail['last'].values[1] < tail['LOWER_BB'].values[1]
            # sell = tail['last'].values[1] > tail['UPPER_BB'].values[1]

            self._set_positions(buy, sell, 'something')

        return full_mkt_data

    def calc_index(self, full_mkt_data):
        """

        :param full_mkt_data: <Dataframe>
        :return:
        """
        full_mkt_data = self.apply_ema(full_mkt_data)
        full_mkt_data.sort_values(by=self.ema_stat_key, ascending=False, inplace=True, na_position='last')
        index_data = full_mkt_data.head(self.index_depth)
        total = index_data[self.ema_stat_key].sum()
        index_data[self.pct_weight_key] = index_data[self.ema_stat_key] / total

        # exp_12 = df.ewm(span=20, min_period=12, adjust=False).mean()

    def apply_ema(self, mkt_data):
        mkt_data = mkt_data.sort_values('id').reset_index().drop(columns=['index'])
        ema_series = mkt_data.groupby(['id']).apply(self.app).reset_index().rename(columns={'market_cap_usd': 'market_cap_usd_EMA'})
        mkt_data = pd.concat([mkt_data, ema_series], axis=1, join_axes=[mkt_data.index])
        return mkt_data

    def app(self, x):
        return x['market_cap_usd'].ewm(span=self.ema_window).mean()
