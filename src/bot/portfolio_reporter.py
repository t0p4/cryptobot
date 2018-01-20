import pandas as pd
from exchange_adaptor import ExchangeAdaptor
from src.utils.utils import calculate_base_value


class PortfolioReporter(ExchangeAdaptor):
    def __init__(self, pg, exchanges):
        ExchangeAdaptor.__init__(self)
        self.pg = pg
        self.exchanges = exchanges
        self.p_report = {}
        self.prev_daily = self.get_prev_daily()
        self.prev_weekly = self.get_prev_weekly()
        self.initial_investments = self.get_initial_investments()
        """
            {'LTC': <DataFrame>, 'XLM': <DataFrame>, ...}
        """
        self.aggregate_portfolio = pd.DataFrame()
        """
            {'LTCBTC': 0.023, 'XLMETH': 0.0093, ...}
        """
        self.current_exchange_rates = pd.DataFrame

    def get_initial_investments(self):
        return self.pg.get_initial_investments()

    def get_exchange_adaptor(self, exchange):
        return self.exchange_adaptors[exchange]()

    def generate_p_report(self):
        self.update_and_aggregate_exchange_portfolios()
        self.calculate_percentage_holdings()
        self.save_p_report()

    def get_btc_usd_rate(self):
        """TODO: pull from gdax & gemini, return best rate and which exchange"""
        btc_usd_rate = 11500
        exchange = 'gemini'
        return btc_usd_rate, exchange

    def get_eth_usd_rate(self):
        """TODO: pull from gdax & gemini, return best rate and which exchange"""
        eth_usd_rate = 1000
        exchange = 'gemini'
        return eth_usd_rate, exchange

    def get_prev_daily(self):
        return self.pg.get_prev_daily()

    def get_prev_weekly(self):
        return self.pg.get_prev_weekly()

    def update_and_aggregate_exchange_portfolios(self):
        for exchange in self.exchanges:
            current_exchange_balances = self.get_exchange_balances(exchange)
            for cur_idx, cur_asset_data in current_exchange_balances.iterrows():
                coin_idx = self.aggregate_portfolio[self.aggregate_portfolio['currency'] == cur_asset_data['currency']].index
                if coin_idx:
                    cur_amt = self.aggregate_portfolio.loc[coin_idx, 'total']
                    self.aggregate_portfolio.set_value(coin_idx, 'total', cur_amt + cur_asset_data['balance'])
                else:
                    self.aggregate_portfolio.append(cur_asset_data)

        self.p_report['total_coins'] = self.aggregate_portfolio.length
        if self.prev_daily:
            self.p_report['total_coins_change'] = self.p_report['total_coins'] - self.prev_daily['total_coins']

        self.calculate_portfolio_totals()

    def calculate_portfolio_totals(self):
        btc_usd_rate, btc_usd_rate_exchange = self.get_btc_usd_rate()
        eth_usd_rate, eth_usd_rate_exchange = self.get_eth_usd_rate()

        est_btc = self.aggregate_portfolio['est_btc'].sum()
        est_eth = self.aggregate_portfolio['est_eth'].sum()
        est_usd_btc = calculate_base_value(est_btc, btc_usd_rate)
        est_usd_eth = calculate_base_value(est_eth, eth_usd_rate)

        self.p_report['est_eth'] = est_eth
        self.p_report['est_btc'] = est_btc
        self.p_report['est_usd'] = max(est_usd_btc, est_usd_eth)

        if self.prev_daily:
            self.calculate_daily_changes()
        if self.prev_weekly:
            self.calculate_weekly_changes()
        self.calculate_rois()

    def calculate_daily_changes(self):
        self.p_report['est_btc_change_daily'] = self.p_report['est_btc'] - self.prev_daily['est_btc']
        self.p_report['est_btc_pct_change_daily'] = self.p_report['est_btc_change_daily'] / self.prev_daily['est_btc']

        self.p_report['est_eth_change_daily'] = self.p_report['est_eth'] - self.prev_daily['est_eth']
        self.p_report['est_eth_pct_change_daily'] = self.p_report['est_eth_change_daily'] / self.prev_daily['est_eth']

        self.p_report['est_usd_change_daily'] = self.p_report['est_usd'] - self.prev_daily['est_usd']
        self.p_report['est_usd_pct_change_daily'] = self.p_report['est_usd_change_daily'] / self.prev_daily['est_usd']

    def calculate_weekly_changes(self):
        self.p_report['est_btc_change_weekly'] = self.p_report['est_btc'] - self.prev_weekly['est_btc']
        self.p_report['est_btc_pct_change_weekly'] = self.p_report['est_btc_change_weekly'] / self.prev_weekly['est_btc']

        self.p_report['est_eth_change_weekly'] = self.p_report['est_eth'] - self.prev_weekly['est_eth']
        self.p_report['est_eth_pct_change_weekly'] = self.p_report['est_eth_change_weekly'] / self.prev_weekly['est_eth']

        self.p_report['est_usd_change_weekly'] = self.p_report['est_usd'] - self.prev_weekly['est_usd']
        self.p_report['est_usd_pct_change_weekly'] = self.p_report['est_usd_change_weekly'] / self.prev_weekly['est_usd']

    def calculate_rois(self):
        self.p_report['current_roi_btc'] = self.p_report['est_btc'] - self.initial_investments['est_btc']
        self.p_report['current_roi_pct_btc'] = self.p_report['current_roi_btc'] / self.initial_investments['est_btc']

        self.p_report['current_roi_eth'] = self.p_report['est_eth'] - self.initial_investments['est_eth']
        self.p_report['current_roi_pct_eth'] = self.p_report['current_roi_eth'] / self.initial_investments['est_eth']

        self.p_report['current_roi_usd'] = self.p_report['est_usd'] - self.initial_investments['est_usd']
        self.p_report['current_roi_pct_usd'] = self.p_report['current_roi_usd'] / self.initial_investments['est_usd']

    def calculate_percentage_holdings(self):
        for idx, row in self.aggregate_portfolio.iterrows():
            {
                "symbol": "LTCBTC",
                "price": "4.00000200"
            },
            tickers = self.get_all_tickers(exchange)

    def save_p_report(self):
        self.pg.save_p_report(self.aggregate_portfolio)