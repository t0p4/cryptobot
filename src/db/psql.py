import datetime
from time import mktime

import pandas as pd
import psycopg2
from psycopg2.extensions import AsIs
import os
import numpy

from src.utils.logger import Logger
from src.db.table_names import TABLE_NAMES

log = Logger(__name__)


class PostgresConnection:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.run_type = os.getenv('RUN_TYPE', 'BACKTEST')

    def table_name(self, table_type):
        return TABLE_NAMES[table_type][self.run_type]

    def _exec_query(self, query, params):
        ###
        # EXECUTES A QUERY ON THE DATABASE, RETURNS NO DATA
        ###
        self.conn = psycopg2.connect("dbname=cryptobot user=patrickmckelvy")
        self.cur = self.conn.cursor()
        try:
            self.cur.execute(query, params)
        except Exception as e:
            log.error('*** POSTGRES ERROR ***')
            log.error(e)

        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def _fetch_query(self, query, params):
        ###
        # EXECUTES A FETCHING QUERY ON THE DATABASE, RETURNS A DATAFRAME
        ###
        self.conn = psycopg2.connect("dbname=cryptobot user=patrickmckelvy")
        self.cur = self.conn.cursor()
        result = None
        try:
            self.cur.execute(query, params)
            column_names = [desc[0] for desc in self.cur.description]
            result = pd.DataFrame(self.cur.fetchall(), columns=column_names)
        except Exception as e:
            log.error('*** POSTGRES ERROR ***')
            log.error(e)

        self.conn.commit()
        self.cur.close()
        self.conn.close()
        return result

    def save_trade(self, order_type, market, quantity, rate, uuid, timestamp):
        log.debug('{PSQL} == SAVE trade ==')
        fmt_str = "('{order_type}','{market}',{quantity},{rate},'{uuid}','{base_currency}','{market_currency}','{timestamp}')"
        columns = "order_type, market, quantity, rate, uuid, base_currency, market_currency, timestamp"
        market_currencies = market.split('-')
        values = {
            "order_type": order_type,
            "market": market,
            "quantity": quantity,
            "rate": rate,
            "uuid": uuid,
            "base_currency": market_currencies[0],
            "market_currency": market_currencies[1],
            "timestamp": timestamp
        }
        params = {
            "columns": AsIs(columns),
            "values": AsIs(fmt_str.format(**values))
        }
        query = """ INSERT INTO """ + self.table_name('save_trade') + """ (%(columns)s) VALUES %(values)s; """
        self._exec_query(query, params)
        return values

    def save_summaries(self, summaries):
        log.debug('{PSQL} == SAVE market summaries ==')
        fmt_str = "({volume},{last},{opensellorders},{bid},{openbuyorders},'{marketname}',{ask},{basevolume},'{saved_timestamp}',{ticker_nonce})"
        columns = "volume,last,opensellorders,bid,openbuyorders,marketname,ask,basevolume,saved_timestamp,ticker_nonce"
        values = AsIs(','.join(fmt_str.format(**summary) for summary in summaries))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('save_summaries') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def save_markets(self, markets):
        log.debug('{PSQL} == SAVE markets ==')
        fmt_str = "('{marketcurrency}','{basecurrency}','{marketcurrencylong}','{basecurrencylong}',{mintradesize},'{marketname}',{isactive},'{logourl}')"
        columns = "marketcurrency,basecurrency,marketcurrencylong,basecurrencylong,mintradesize,marketname,isactive,logourl"
        values = AsIs(','.join(fmt_str.format(**market) for market in markets))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('save_markets') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def save_currencies(self, markets):
        log.debug('{PSQL} == SAVE currencies ==')
        fmt_str = "('{currency}','{currencylong}',{minconfirmation},{txfee},{isactive},'{cointype}','{baseaddress}')"
        columns = "currency,currencylong,minconfirmation,txfee,isactive,cointype,baseaddress"
        values = AsIs(','.join(fmt_str.format(**market) for market in markets))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('save_currencies') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def save_historical_data(self, data):
        log.debug('{PSQL} == SAVE historical data ==')
        fmt_str = '(%s,%s,%s,%s,%s,%s,%s,%s)'
        columns = 'timestamp,open,high,low,close,volume_btc,volume_usd,weighted_price'
        values = AsIs(','.join(fmt_str % tuple(row) for row in data))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO btc_historical (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def get_historical_data(self, start_date, end_date):
        log.debug('{PSQL} == GET historical data ==')
        params = {
            "start_date": mktime(start_date.timetuple()),
            "end_date": mktime(end_date.timetuple())
        }
        query = """
            SELECT open, high, low, close, volume_btc, volume_usd, timestamp FROM btc_historical
            WHERE timestamp >= %(start_date)s AND timestamp < %(end_date)s
            ORDER BY timestamp ASC ;
        """
        return self._fetch_query(query, params)

    def get_market_summaries_by_timestamp(self, target_timestamp):
        log.debug('{PSQL} == GET market summaries ==')
        params = {
            'target_timestamp': target_timestamp
        }
        query = """
            SELECT marketname, last, bid, ask, saved_timestamp FROM market_summaries
            WHERE saved_timestamp = {target_timestamp} ;
        """
        return self._fetch_query(query, params)

    def get_market_summaries_by_ticker(self, tick, market_names):
        log.debug('{PSQL} == GET market summaries by ticker ==')
        params = {
            'ticker_nonce': tick,
            'market_names': market_names
        }
        query = """
            SELECT marketname, last, bid, ask, saved_timestamp, volume FROM fixture_market_summaries
            WHERE ticker_nonce = %(ticker_nonce)s AND marketname IN %(market_names)s
            ;
        """
        return self._fetch_query(query, params)

    def get_fixture_markets(self, base_currencies):
        log.debug('{PSQL} == GET fixture markets ==')
        fmt_str = "(%(currencies)s)"
        columns = "currencies"
        values = AsIs(','.join(fmt_str.format(currency) for currency in base_currencies))
        params = {
            'base_currencies': tuple(base_currencies)
        }
        query = """
            SELECT * FROM fixture_markets
            WHERE basecurrency IN ('ETH', 'BTC');
        """
        return self._fetch_query(query, params)

    def get_fixture_currencies(self):
        log.debug('{PSQL} == GET fixture markets ==')
        params = {}
        query = """ SELECT * FROM fixture_currencies ; """
        return self._fetch_query(query, params)

    def get_all_trade_data(self):
        log.debug('{PSQL} == GET trade data ==')
        params = {}
        query = """ SELECT * FROM """ + self.table_name('trade_data')
        return self._fetch_query(query, params)

    def get_most_recent_trades(self):
        log.debug('{PSQL} == GET most recent trade data ==')
        params = {}
        query = """
            SELECT * FROM """ + self.table_name('trade_data') + """
            WHERE trade_time == MAX(trade_time) GROUP BY market_currency
            ;
        """
        return self._fetch_query(query, params)

    def get_full_report(self, report_date):
        report_overview = self.get_report_overview(report_date)
        if report_overview.empty:
            return None, None
        else:
            report_assets = self.get_report_assets(report_overview.loc[0, 'report_id'])
            return report_overview, report_assets

    def get_report_overview(self, report_date):
        log.debug('{PSQL} == GET most recent portfolio report data ==')
        params = {
            'report_date': report_date
        }
        query = """
            SELECT * FROM """ + self.table_name('portfolio_reports') + """
            WHERE report_date = %(report_date)s
            ;
        """
        return self._fetch_query(query, params)

    def get_report_assets(self, report_id):
        log.debug('{PSQL} == GET most recent portfolio report asset data ==')
        params = {
            'report_id': report_id
        }
        query = """
            SELECT * FROM """ + self.table_name('portfolio_assets') + """
            WHERE report_id = %(report_id)s
            ;
        """
        return self._fetch_query(query, params)

    # REFACTORING TABLES #

    def save_cmc_tickers(self, tickers, extra_columns):
        log.debug('{PSQL} == SAVE tickers ==')
        add_fmt_str = ''
        add_columns = ''
        for col in extra_columns:
            add_fmt_str += ',{' + col + '}'
            add_columns += ',' + col
        fmt_str = """
                (
                    '{id}',
                    '{name}',
                    '{symbol}',
                    '{rank}',
                    {price_btc},
                    {price_usd},
                    {daily_volume_usd},
                    {market_cap_usd},
                    {available_supply},
                    {total_supply},
                    {percent_change_1h},
                    {percent_change_24h},
                    {percent_change_7d},
                    {last_updated},
                    {nonce}""" + add_fmt_str + """
                )
                """
        columns = """
                    id,
                    name,
                    symbol,
                    rank,
                    price_btc,
                    price_usd,
                    daily_volume_usd,
                    market_cap_usd,
                    available_supply,
                    total_supply,
                    percent_change_1h,
                    percent_change_24h,
                    percent_change_7d,
                    last_updated,
                    nonce""" + add_columns + """
                """
        tickers = tickers.where(pd.notna(tickers), tickers.mean(), axis='columns')
        values = AsIs(','.join(fmt_str.format(**ticker) for idx, ticker in tickers.iterrows()))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('save_cmc_tickers') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def pull_cmc_tickers(self, nonce):
        log.debug('{PSQL} == GET BACKTEST cmc tickers ==')
        params = {
            'nonce': nonce
        }
        query = """
            SELECT * FROM """ + self.table_name('save_cmc_tickers') + """
            WHERE nonce = %(nonce)s;
        """
        return self._fetch_query(query, params)

    def save_cmc_historical_data(self, tickers):
        log.debug('{PSQL} == SAVE historical cmc data ==')
        fmt_str = """
                (
                    '{coin}',
                    '{id}',
                    '{date}',
                    {open},
                    {high},
                    {low},
                    {close},
                    {market_cap},
                    {volume},
                    {average}
                )
                """
        columns = """
                    coin,
                    id,
                    date,
                    open,
                    high,
                    low,
                    close,
                    market_cap,
                    volume,
                    average
                """
        tickers = tickers.where(pd.notna(tickers), tickers.mean(), axis='columns')
        values = AsIs(','.join(fmt_str.format(**ticker) for idx, ticker in tickers.iterrows()))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('cmc_historical_data') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def get_cmc_historical_data(self, date):
        log.debug('{PSQL} == GET BACKTEST cmc historical data ==')
        query = """SELECT * FROM """ + self.table_name('cmc_historical_data') + """ WHERE date = '""" + date + """';"""
        return self._fetch_query(query, {})

    def save_cmc_coin_metadata(self, metadata):
        log.debug('{PSQL} == SAVE cmc coin meta data ==')
        fmt_str = """
                (
                    '{coin}',
                    '{id}',
                    '{name}'
                )
                """
        columns = """
                    coin,
                    id,
                    name
                """
        values = AsIs(','.join(fmt_str.format(**data) for data in metadata))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('cmc_coin_metadata') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def get_cmc_coin_metadata(self):
        log.debug('{PSQL} == GET BACKTEST cmc historical data ==')
        query = """SELECT * FROM """ + self.table_name('cmc_coin_metadata')
        return self._fetch_query(query, {})

    def save_tickers(self, tickers):
        log.debug('{PSQL} == SAVE tickers ==')
        fmt_str = """
        (
            '{pair}',
            '{base_coin}',
            '{mkt_coin}',
            {open},
            {high},
            {low},
            {close},
            {bid},
            {ask},
            {last},
            {vol_base},
            {vol_mkt},
            {timestamp},
            '{exchange}',
            {ticker_nonce}
        )
        """
        columns = """
            pair,
            base_coin,
            mkt_coin,
            open,
            high,
            low,
            close,
            bid,
            ask,
            last,
            vol_base,
            vol_mkt,
            timestamp,
            exchange,
            ticker_nonce
        """
        values = AsIs(','.join(fmt_str.format(**ticker) for ticker in tickers))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('save_tickers') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def save_trade_data(self, trade_data):
        log.debug('{PSQL} == SAVE historical_trade_data ==')
        fmt_str = """
        (
            '{order_id}',
            '{exchange}',
            '{order_type}',
            '{pair}',
            '{base_coin}',
            '{mkt_coin}',
            '{trade_direction}',
            '{is_live}',
            '{is_cancelled}',
            {original_amount},
            {executed_amount},
            {remaining_amount},
            {price},
            {avg_price},
            {rate_btc},
            {rate_eth},
            {rate_usd},
            {cost_avg_btc},
            {cost_avg_eth},
            {cost_avg_usd},
            {analyzed},
            {timestamp},
            {save_time}
        )
        """

        columns = """
            order_id,
            exchange,
            order_type,
            pair,
            base_coin,
            mkt_coin,
            side,
            is_live,
            is_cancelled,
            original_amount,
            executed_amount,
            remaining_amount,
            price,
            avg_price,
            rate_btc,
            rate_eth,
            rate_usd,
            cost_avg_btc,
            cost_avg_eth,
            cost_avg_usd,
            analyzed,
            timestamp,
            save_time
        """
        values = AsIs(','.join(fmt_str.format(**trade) for trade in trade_data))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('save_order') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def save_portfolio_report(self, portfolio_report):
        fmt_str = """(
                    {total_coins},
                    {total_coins_change},
                    {current_roi_btc},
                    {current_roi_pct_btc},
                    {current_roi_eth},
                    {current_roi_pct_eth},
                    {current_roi_usd},
                    {current_roi_pct_usd},
                    {est_btc},
                    {est_btc_change_daily},
                    {est_btc_pct_change_daily},
                    {est_btc_change_weekly},
                    {est_btc_pct_change_weekly},
                    {est_eth},
                    {est_eth_change_daily},
                    {est_eth_pct_change_daily},
                    {est_eth_change_weekly},
                    {est_eth_pct_change_weekly},
                    {est_usd},
                    {est_usd_change_daily},
                    {est_usd_pct_change_daily},
                    {est_usd_change_weekly},
                    {est_usd_pct_change_weekly},
                )"""
        columns = """
                    total_coins,
                    total_coins_change,
                    current_roi_btc,
                    current_roi_pct_btc,
                    current_roi_eth,
                    current_roi_pct_eth,
                    current_roi_usd,
                    current_roi_pct_usd,
                    est_btc,
                    est_btc_change_daily,
                    est_btc_pct_change_daily,
                    est_btc_change_weekly,
                    est_btc_pct_change_weekly,
                    est_eth,
                    est_eth_change_daily,
                    est_eth_pct_change_daily,
                    est_eth_change_weekly,
                    est_eth_pct_change_weekly,
                    est_usd,
                    est_usd_change_daily,
                    est_usd_pct_change_daily,
                    est_usd_change_weekly,
                    est_usd_pct_change_weekly
                """
        values = fmt_str.format(**portfolio_report)
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('portfolio_reports') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)

    def save_portfolio_assets(self, portfolio_assets):
        log.debug('{PSQL} == SAVE portfolio report ==')
        fmt_str = """(
            {report_id},
            '{currency}',
            {total},
            {total_holdings_change},
            {pct_holdings_change},
            {portfolio_pct},
            {cost_avg},
            {current_roi_btc},
            {current_roi_pct_btc},
            {current_roi_eth},
            {current_roi_pct_eth},
            {current_roi_usd},
            {current_roi_pct_usd},
            {est_btc},
            {est_btc_change_daily},
            {est_btc_pct_change_daily},
            {est_btc_change_weekly},
            {est_btc_pct_change_weekly},
            {est_eth},
            {est_eth_change_daily},
            {est_eth_pct_change_daily},
            {est_eth_change_weekly},
            {est_eth_pct_change_weekly},
            {est_usd},
            {est_usd_change_daily},
            {est_usd_pct_change_daily},
            {est_usd_change_weekly},
            {est_usd_pct_change_weekly},
        )"""
        columns = """
            report_id,
            currency,
            total,
            total_holdings_change,
            pct_holdings_change,
            portfolio_pct,
            cost_avg,
            current_roi_btc,
            current_roi_pct_btc,
            current_roi_eth,
            current_roi_pct_eth,
            current_roi_usd,
            current_roi_pct_usd,
            est_btc,
            est_btc_change_daily,
            est_btc_pct_change_daily,
            est_btc_change_weekly,
            est_btc_pct_change_weekly,
            est_eth,
            est_eth_change_daily,
            est_eth_pct_change_daily,
            est_eth_change_weekly,
            est_eth_pct_change_weekly,
            est_usd,
            est_usd_change_daily,
            est_usd_pct_change_daily,
            est_usd_change_weekly,
            est_usd_pct_change_weekly
        """
        values = AsIs(','.join(fmt_str.format(**asset) for asset in portfolio_assets))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO """ + self.table_name('portfolio_assets') + """ (%(columns)s) VALUES %(values)s ; """
        self._exec_query(query, params)
