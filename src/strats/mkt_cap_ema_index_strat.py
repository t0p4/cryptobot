import pandas as pd
from src.strats.base_strat import BaseStrategy
from src.exceptions import StratError
from src.utils.logger import Logger
from datetime import datetime
from src.utils.utils import scale_features
import numpy
log = Logger(__name__)


class EMAIndexStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)
        self.sma_window = options['sma_window']
        self.index_depth = options['index_depth']
        self.pre_index_depth = options['pre_index_depth']
        self.ema_stat_key = self.stat_key + self.ema_suffix
        self.ema_diff_stat_key = self.ema_stat_key + '_diff'
        self.ema_diff_avg_stat_key = self.ema_diff_stat_key + '_avg'
        self.stat_weight = options['weights']['stat_weight']
        self.ema_diff_avg_weight = options['weights']['ema_diff_avg_weight']
        if self.stat_weight + self.ema_diff_avg_weight != 1:
            raise StratError('MKT CAP EMA strat', 'init', 'weights dont add to 1')
        self.stat_top_percentile = options['stat_top_percentile']
        self.pct_weight_key = self.stat_key + self.pct_weight_suffix
        self.positions = None
        self.add_columns = [self.ema_stat_key, self.pct_weight_key]
        self.trade_threshold_pct = options['trade_threshold_pct']
        self.blacklist = options['blacklist']
        self.whitelist = options['whitelist']
        self.index_data = None
        self.score_key = 'index_score'
        self.vol_avg_key = 'volume_avg'
        self.mkt_cap_avg_key = 'mkt_cap_avg'

        # configure name for ML stat backtesting
        self.name = options['name'] + '_' + str(self.stat_weight) + '/' + str(self.ema_diff_avg_weight)

    def handle_data_index(self, full_mkt_data, holdings_data, index_coins=None, index_date=None):
        """
        :param full_mkt_data: <DataFrame> full market prices from cmc
        :param holdings_data: <DataFrame> aggregate account balances
        :param index_coins: <List> current coins in index
                            * index_coins=None to reset the index (calculate new index makeup)
        :return:
        """
        if index_date is None:
            index_date = full_mkt_data['date'].max()
        self.index_data = full_mkt_data
        # check how many values exist per coin
        if full_mkt_data.groupby('id').agg('count').loc['Bitcoin', 'coin'] >= self.ema_window:
            self.calc_index(index_date, index_coins=index_coins)
            self.calc_deltas(holdings_data)
        return self.index_data

    def calc_index(self, index_date, index_coins=None):
        """
        :param full_mkt_data: <DataFrame> full market prices from cmc
        :param index_coins: <List> current coins in index
                            * index_coins=None to reset the index (calculate new index makeup)
        :return: <DataFrame> index data
        """
        # remove bottom percentile
        if index_coins is None:
            # remove low volume coins
            self.index_data = self.index_data.groupby('id').apply(self.apply_avg_monthly_volume)
            self.index_data = self.index_data.groupby('id').apply(self.apply_avg_monthly_mkt_cap)
            index_on_date = self.index_data[self.index_data['date'] == index_date]

            vol_avg_coins_to_drop = index_on_date[index_on_date[self.vol_avg_key] < 1000]['id']
            mkt_cap_avg_coins_to_drop = index_on_date[index_on_date[self.mkt_cap_avg_key] < 10000000]['id']
            coins_to_drop = mkt_cap_avg_coins_to_drop + vol_avg_coins_to_drop

            self.index_data = self.index_data.drop(self.index_data[self.index_data['id'].isin(coins_to_drop.values)].index)

            num_in_top_percentile = round(len(self.index_data[self.index_data['date'] == index_date]) * (1 - self.stat_top_percentile))
            # sort by stat key on index date, then take top percentile coins, keep those coins in self.index_data
            top_percentile_coins = self.index_data[self.index_data['date'] == index_date].sort_values(by=[self.stat_key], ascending=False)[
                'id'].unique()[:num_in_top_percentile]
            self.index_data = self.index_data[self.index_data['id'].isin(top_percentile_coins)]
            # remove blacklist, sort, apply ema calcs
            self.index_data = self.index_data.drop(self.index_data[self.index_data['coin'].isin(self.blacklist)].index)

        self.index_data.sort_values(by=['id', 'date'], inplace=True)
        self.apply_ema()
        self.apply_ema_diff()
        # at this point only the latest data for each coin is relevant for the index score
        self.index_data = self.index_data[self.index_data['date'] == index_date]
        self.apply_index_score()

        # calc pct_weights
        # total = self.index_data[self.stat_key].sum()
        # self.index_data[self.pct_weight_key] = self.index_data[self.stat_key] / total

        # ema_index_data = full_mkt_data.sort_values(self.ema_stat_key, ascending=False).head(self.index_depth)
        # total = ema_index_data[self.ema_stat_key].sum()
        # ema_index_data[self.pct_weight_key] = ema_index_data[self.ema_stat_key] / total
        #
        # index_data['in_index'] = True
        if index_coins is not None:
            self.index_data = self.index_data[self.index_data['id'].isin(index_coins)]
        else:
            self.index_data = self.index_data.sort_values(by=['index_score'], ascending=False).head(self.index_depth)

        score_total = self.index_data[self.score_key].sum()
        self.index_data['index_pct'] = self.index_data[self.score_key] / score_total
        self.index_data.rename(columns={'close': 'rate_usd'}, inplace=True)
        self.index_data = self.index_data[['id', 'index_pct', 'coin', 'rate_usd']]

    def calc_deltas(self, holdings_data):
        """
        :param index_data: <Dataframe> columns = ['id', 'index_pct']
        :param holdings_data: <Dataframe> columns = ['id', 'balance', 'balance_btc']
        :return: <Dataframe> columns = ['id', 'balance', 'index_pct', 'balance_btc', 'index_btc', 'delta_btc', 'delta_pct', 'should_trade']
        """
        self.index_data = pd.merge(self.index_data, holdings_data, on='id', how='outer')
        self.index_data = self.index_data.rename(columns={'coin_x': 'coin'}).drop(columns=['coin_y'])
        self.index_data['balance'] = self.index_data['balance'].replace(numpy.NaN, 0)
        self.index_data['balance_usd'] = self.index_data['balance'] * self.index_data['rate_usd']
        total_usd = self.index_data.head(self.index_depth)['balance_usd'].sum()
        self.index_data['balance_pct'] = self.index_data['balance_usd'] / total_usd
        self.index_data['index_usd'] = self.index_data['index_pct'] * total_usd
        self.index_data['delta_usd'] = self.index_data['index_usd'] - self.index_data['balance_usd']
        self.index_data['delta_pct'] = self.index_data['delta_usd'] / self.index_data['balance_usd']
        self.index_data['delta_coins'] = (self.index_data['index_pct'] - self.index_data['balance_pct']) * total_usd / self.index_data['rate_usd']
        # transaction_diff = ( index_pct - holdings_pct ) * total_portfolio_value / current_coin_usd_rate
        # self.index_data['should_trade'] = self.index_data['delta_pct'] >= self.trade_threshold_pct
        # self.index_data = self.index_data[self.index_data['should_trade']]

    def apply_avg_monthly_volume(self, df):
        df[self.vol_avg_key] = df.sort_values(by=['date'], ascending=True)['volume'].rolling(30).mean()
        return df

    def apply_avg_monthly_mkt_cap(self, df):
        df[self.mkt_cap_avg_key] = df.sort_values(by=['date'], ascending=True)['market_cap'].rolling(30).mean()
        return df

    def apply_ema(self):
        log.info('APPLY EMA')
        ema_series = self.index_data.groupby(['id']).apply(self.ema_calc)
        ema_series = ema_series.reset_index().rename(columns={self.stat_key: self.ema_stat_key}).drop(columns=['id']).set_index('level_1')
        self.index_data= self.index_data.merge(ema_series, left_index=True, right_index=True)

    def apply_ema_diff(self):
        log.info('APPLY EMA DIFF')
        ema_diff_series = self.index_data.groupby(['id']).apply(self.ema_diff_calc)
        ema_diff_series = ema_diff_series.reset_index().rename(columns={0: self.ema_diff_stat_key}).drop(
            columns=['id']).set_index('level_1')
        self.index_data = self.index_data.merge(ema_diff_series, left_index=True, right_index=True)
        self.index_data[self.ema_diff_avg_stat_key] = self.index_data[self.ema_diff_stat_key].rolling(self.sma_window).mean()

    def ema_calc(self, x):
        return x[self.stat_key].ewm(span=self.ema_window).mean()

    def ema_diff_calc(self, x):
        return (x[self.stat_key] - x[self.ema_stat_key]) / x[self.ema_stat_key]

    def apply_index_score(self):
        log.info('APPLY INDEX SCORE')
        # remove na's
        self.index_data.dropna(inplace=True)
        # # grab first index depth
        # self.index_data = self.index_data.sort_values(by=[self.stat_key], ascending=False).head(self.pre_index_depth)
        # scale features of relevant data
        self.index_data[self.stat_key] = scale_features(self.index_data[self.stat_key])
        self.index_data[self.ema_diff_avg_stat_key] = scale_features(self.index_data[self.ema_diff_avg_stat_key])
        # apply weights
        self.index_data['index_score'] = (self.index_data[self.stat_key] * self.stat_weight) + (self.index_data[self.ema_diff_avg_stat_key] * self.ema_diff_avg_weight)
