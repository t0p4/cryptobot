from datetime import datetime, timedelta
from time import mktime

import pandas as pd

from src.utils.logger import Logger

log = Logger(__name__)

INF = 999999999999999


def is_first_of_the_month(date):
    return date.day == 1


def is_fifteenth_of_the_month(date):
    return date.day == 15


def is_valid_market(mkt_name, currencies):
    mkts = mkt_name.split('-')
    return mkts[0] in currencies


def is_valid_pair(pair, valid_bases, valid_mkts):
    return pair['base_coin'] in valid_bases and pair['mkt_coin'] in valid_mkts


def add_saved_timestamp(data, tick):
    timestamp = datetime.utcnow().isoformat()

    def add_timestamp(series):
        series['saved_timestamp'] = timestamp
        series['ticker_nonce'] = tick
        return series

    return map(add_timestamp, data)


def ohlc_hack(data):
    shape = data.shape
    length = shape[0]
    if length > 1:
        data.loc[length - 1, 'close'] = data.loc[length - 1, 'last']
        data.loc[length - 1, 'open'] = data.loc[length - 2, 'close']
    return data


def normalize_columns(data):
    data.columns = map(str, data.columns)
    data.columns = map(str.lower, data.columns)
    return data


def normalize_index(data):
    data.index = map(str, data.index)
    data.index = map(str.lower, data.index)
    return data


def capitalize_index(data):
    data.index = map(str, data.index)
    data.index = map((lambda idx: idx[:1].upper() + idx[1:]), data.index)
    return data


def get_coins_from_market(market):
    coins = market.split('-')
    base_coin = coins[0]
    mkt_coin = coins[1]
    return base_coin, mkt_coin


def normalize_inf_rows(data):
    log.info('NORMALIZING DATA')
    for index, row in data.iterrows():
        if row['open'] > INF:
            idx = index
            if idx == 0:
                while data.loc[idx, 'open'] > INF:
                    idx += 1
                idx += 1
            data.loc[index] = data.loc[idx - 1]
    return data


def normalize_inf_rows_dicts(data):
    log.info('NORMALIZING DATA')
    for index, row in enumerate(data):
        if row[1] > INF:
            idx = index
            if idx == 0:
                while data[idx][1] > INF:
                    idx += 1
                idx += 1
            data[index] = data[idx - 1][:]
    return data


def calculate_base_currency_volume(volume, rate):
    return volume * rate


def calculate_base_value(amt, rate):
    return amt * rate


def get_past_date(minus_days):
    return datetime.today() - timedelta(days=minus_days)


def is_eth(coin):
    return coin.lower() == 'eth'


def is_btc(coin):
    return coin.lower() == 'btc'


def merge_2_dicts(dict1, dict2):
    new_dict = dict1.copy()
    new_dict.update(dict2)
    return new_dict
