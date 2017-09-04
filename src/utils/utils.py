import datetime

import pandas as pd

from src.utils.logger import Logger

log = Logger(__name__)

INF = 999999999999999


def is_valid_market(mkt_name, currencies):
    return mkt_name.split('-')[0] in currencies


def add_saved_timestamp(data):
    length = len(data)
    timestamp = datetime.datetime.now()
    timestamp_series = pd.Series([timestamp] * length)
    data = data.assign(saved_timestamp=timestamp_series.values)
    return data


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