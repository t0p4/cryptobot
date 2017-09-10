import pandas as pd
import datetime

PROCESSED_SUMMARY_TICKERS_FIXTURE = pd.DataFrame([
    {'bid': 1.8, 'ask': 1.8, 'last': 1.8, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 0, 1), 'marketname': 'BTC-LTC'},
    {'bid': 1.9, 'ask': 1.9, 'last': 1.9, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 5, 1), 'marketname': 'BTC-LTC'},
    {'bid': 2, 'ask': 2, 'last': 2, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 10, 1), 'marketname': 'BTC-LTC'},
    {'bid': 2.1, 'ask': 2.1, 'last': 2.1, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 15, 1), 'marketname': 'BTC-LTC'},
    {'bid': 2.2, 'ask': 2.2, 'last': 2.2, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 20, 1), 'marketname': 'BTC-LTC'},
])