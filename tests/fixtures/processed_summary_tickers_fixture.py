import pandas as pd
import datetime

PROCESSED_SUMMARY_TICKERS_FIXTURE = pd.DataFrame([
    {'bid': 0, 'ask': 0, 'last': 0, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 0, 1), 'marketname': 'BTC-LTC'},
    {'bid': 1, 'ask': 1, 'last': 1, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 5, 1), 'marketname': 'BTC-LTC'},
    {'bid': 2, 'ask': 2, 'last': 2, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 10, 1), 'marketname': 'BTC-LTC'},
    {'bid': 3, 'ask': 3, 'last': 3, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 15, 1), 'marketname': 'BTC-LTC'},
    {'bid': 4, 'ask': 4, 'last': 4, 'saved_timestamp': datetime.datetime(2017, 1, 1, 1, 20, 1), 'marketname': 'BTC-LTC'},
])