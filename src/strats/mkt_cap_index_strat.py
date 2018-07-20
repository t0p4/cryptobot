import pandas as pd
from src.strats.base_strat import BaseStrategy
from src.exceptions import StratError
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
        self.blacklist = options['blacklist']
        self.whitelist = options['whitelist']

    def handle_data_index(self, full_mkt_data, holdings_data, index_coins=None):
        """
        :param full_mkt_data: <DataFrame> full market prices from cmc
        :param holdings_data: <DataFrame> aggregate account balances
        :param index_coins: <List> current coins in index
                            * index_coins=None to reset the index (calculate new index makeup)
        :return:
        """
        # if full_mkt_data.groupby('id').agg('count').loc['bitcoin', 'symbol'] >= self.sma_window:
        index_data = self.calc_index(full_mkt_data, index_coins)
        index_data = self.calc_deltas(index_data, holdings_data)
        return index_data

    def calc_index(self, full_mkt_data, index_coins=None):
        """
        :param full_mkt_data: <DataFrame> full market prices from cmc
        :param index_coins: <List> current coins in index
                            * index_coins=None to reset the index (calculate new index makeup)
        :return: <DataFrame> index data
        """

        full_mkt_data = full_mkt_data.drop(full_mkt_data[full_mkt_data['id'].isin(self.blacklist)].index)

        if self.whitelist is not None:
            full_mkt_data = full_mkt_data[full_mkt_data['id'].isin(self.whitelist)]

        if index_coins is None:
            index_data = full_mkt_data.sort_values(self.stat_key, ascending=False).head(self.index_depth)
        else:
            index_data = full_mkt_data[full_mkt_data['id'].isin(index_coins)]
            # if len(index_data) != self.index_depth:
            #     err = 'given coins (%s) / index depth (%s) mismatch' % len(index_coins), len(index_data)
            #     raise StratError(self.name, "calc_index", err)

        stat_total = index_data[self.stat_key].sum()
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
        dataset = pd.merge(index_data, holdings_data, on='id', how='outer')
        dataset = dataset.rename(columns={'coin_x': 'coin'}).drop(columns=['coin_y'])
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
