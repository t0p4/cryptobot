import pandas as pd
from src.strats.base_strat import BaseStrategy
from src.utils.logger import Logger
from datetime import datetime
import numpy
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
        self.trade_threshold_pct = options['trade_threshold_pct']

    def handle_data_index(self, full_mkt_data, holdings_data):
        # if full_mkt_data.groupby('id').agg('count').loc['bitcoin', 'symbol'] >= self.sma_window:
        index_data = self.calc_index(full_mkt_data)
        index_data = self.calc_deltas(index_data, holdings_data)
        return index_data

    def calc_index(self, full_mkt_data):
        """

        :param full_mkt_data: <Dataframe>
        :return:
        """
        # full_mkt_data = self.apply_ema(full_mkt_data)
        # full_mkt_data.sort_values(by=self.ema_stat_key, ascending=False, inplace=True, na_position='last')
        # full_mkt_data = full_mkt_data.groupby(['id']).agg(['last'])
        # full_mkt_data.columns = full_mkt_data.columns.droplevel(1)
        #
        # index_data = full_mkt_data.sort_values(self.stat_key, ascending=False).head(self.index_depth)
        # total = index_data[self.stat_key].sum()
        # index_data[self.pct_weight_key] = index_data[self.stat_key] / total
        #
        # ema_index_data = full_mkt_data.sort_values(self.ema_stat_key, ascending=False).head(self.index_depth)
        # total = ema_index_data[self.ema_stat_key].sum()
        # ema_index_data[self.pct_weight_key] = ema_index_data[self.ema_stat_key] / total

        index_data = full_mkt_data.sort_values(self.stat_key, ascending=False)
        # index_data['in_index'] = True
        stat_total = index_data[self.stat_key].head(self.index_depth).sum()
        index_data['index_pct'] = index_data[self.stat_key] / stat_total
        index_data.rename(columns={'close': 'rate_usd'}, inplace=True)
        return index_data[['id', 'index_pct', 'coin', 'rate_usd']]
        # exp_12 = df.ewm(span=20, min_period=12, adjust=False).mean()

    def calc_deltas(self, index_data, holdings_data):
        """
        :param index_data: <Dataframe> columns = ['id', 'index_pct']
        :param holdings_data: <Dataframe> columns = ['id', 'balance', 'balance_btc']
        :return: <Dataframe> columns = ['id', 'balance', 'index_pct', 'balance_btc', 'index_btc', 'delta_btc', 'delta_pct', 'should_trade']
        """
        dataset = pd.merge(index_data, holdings_data, on='coin', how='outer')
        dataset['balance'] = dataset['balance'].replace(numpy.NaN, 0)
        dataset['balance_usd'] = dataset['balance'] * dataset['rate_usd']
        total_usd = dataset.head(self.index_depth)['balance_usd'].sum()
        dataset['balance_pct'] = dataset['balance_usd'] / total_usd
        dataset['index_usd'] = dataset['index_pct'] * total_usd
        dataset['delta_usd'] = dataset['index_usd'] - dataset['balance_usd']
        dataset['delta_pct'] = dataset['delta_usd'] / dataset['balance_usd']
        dataset['delta_coins'] = (dataset['index_pct'] - dataset['balance_pct']) * total_usd / dataset['rate_usd']
        # transaction_diff = ( index_pct - holdings_pct ) * total_portfolio_value / current_coin_usd_rate
        dataset['should_trade'] = dataset['delta_pct'] >= self.trade_threshold_pct
        return dataset

    def apply_ema(self, mkt_data):
        mkt_data = mkt_data.sort_values('id').reset_index().drop(columns=['index'])
        ema_series = mkt_data.groupby(['id']).apply(self.app).reset_index().rename(columns={self.stat_key: self.ema_stat_key}).drop(columns=['id'])
        mkt_data = pd.concat([mkt_data, ema_series], axis=1, join_axes=[mkt_data.index])
        return mkt_data

    def app(self, x):
        return x[self.stat_key].ewm(span=self.ema_window).mean()
