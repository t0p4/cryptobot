import os
import subprocess
import psycopg2
from psycopg2.extensions import AsIs
from time import sleep
import io
import pandas as pd
import datetime
import dateutil.relativedelta


class PostgresConnection:
    def __init__(self):
        self.conn = None
        self.cur = None

    def _exec_query(self, query, params):
        ###
        # EXECUTES A QUERY ON THE DATABASE, RETURNS NO DATA
        ###
        self.conn = psycopg2.connect("dbname=instabot user=patrickmckelvy")
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
        self.conn = psycopg2.connect("dbname=instabot user=patrickmckelvy")
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
        timestamp = datetime.datetime.now()
        params = {
            "order_type": order_type,
            "market": market,
            "quantity": quantity,
            "rate": rate,
            "timestamp": timestamp,
            "uuid": uuid
        }
        query = """UPDATE orders
                    SET order_type = %(order_type)s, market = %(market)s, quantity=%(quantity),
                     rate = %(rate)s, timestamp = %(timestamp)s, uuid = %(uuid)s
                """
        self._exec_query(query, params)