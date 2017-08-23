import os
import subprocess
import psycopg2
from psycopg2.extensions import AsIs
from time import sleep
import io
import pandas as pd
import datetime
import dateutil.relativedelta
from time import mktime


class PostgresConnection:
    def __init__(self):
        self.conn = None
        self.cur = None

    def _exec_query(self, query, params):
        ###
        # EXECUTES A QUERY ON THE DATABASE, RETURNS NO DATA
        ###
        self.conn = psycopg2.connect("dbname=cryptobot user=patrickmckelvy")
        self.cur = self.conn.cursor()
        try:
            self.cur.execute(query, params)
        except Exception as e:
            print('*** POSTGRES ERROR ***')
            print(e)

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
            print('*** POSTGRES ERROR ***')
            print(e)

        self.conn.commit()
        self.cur.close()
        self.conn.close()
        return result

    def save_trade(self, order_type, market, quantity, rate, uuid):
        print('== SAVE trade ==')
        fmt_str = "('{order_type}','{market}',{quantity},{rate},'{uuid}','{base_currency}','{market_currency}','{timestamp}')"
        columns = "(order_type, market, quantity, rate, uuid, base_currency, market_currency, timestamp)"
        timestamp = datetime.datetime.now()
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
            "values": fmt_str.format(**values)
        }
        query = """ INSERT INTO orders (%(columns)s) VALUES %(values)s; """
        self._exec_query(query, params)

    def save_summaries(self, summaries):
        print('== SAVE market summaries ==')
        fmt_str = "({PrevDay},{Volume},{Last},{OpenSellOrders},'{TimeStamp}',{Bid},'{Created}',{OpenBuyOrders},{High},'{MarketName}',{Low},{Ask},{BaseVolume})"
        columns = "prevday,volume,last,opensellorders,timestamp,bid,created,openbuyorders,high,marketname,low,ask,basevolume"
        for idx, summary in enumerate(summaries):
            summaries[idx]['TimeStamp'] = summary['TimeStamp'].replace('T', ' ').split('.')[0]
            summaries[idx]['Created'] = summary['Created'].replace('T', ' ').split('.')[0]
        values = AsIs(','.join(fmt_str.format(**summary) for summary in summaries))
        params = {
            "columns": AsIs(columns),
            "values": values
        }
        query = """ INSERT INTO summaries (%(columns)s) VALUES %(values)s; """
        self._exec_query(query, params)