from src.exchange.binance.client import Client
from src.exchange.bittrex import Bittrex
from src.exchange.backtest_exchange import BacktestExchange
from src.exchange.coinigy.coinigy_api_rest import CoinigyREST
from src.exchange.gemini import Geminipy
import pandas as pd
from src.utils.conversion_utils import convert_str_columns_to_num, get_usd_rate
from src.utils.utils import is_eth, is_btc
import time
from src.exchange.gdax.public_client import PublicClient as GDaxPub
from datetime import datetime
from src.utils.logger import Logger
from src.utils.rate_limiter import RateLimiter
from src.api.api_utils import format_exchange_pair, format_exchange_start_and_end_times, format_exchange_interval
from src.exceptions import APIRequestError

log = Logger(__name__)


EXCHANGE_ADAPTORS = {
    'binance': Client,
    'bittrex': Bittrex,
    'coinigy': CoinigyREST,
    'backtest': BacktestExchange,
    'gemini': Geminipy,
    'gdax_public': GDaxPub
}

RATE_LIMITERS = {
    'binance': RateLimiter('binance'),
    'gdax_public': RateLimiter('gdax_public')
}


def get_historical_rate(params):
    """1
        gets the desired pair rate from the specified time period
    :param params:
        base_coin: 'BTC'
        mkt_coin: 'USD'
        timestamp: <unix timestamp>
        interval: <num><unit> (1m, 2h, 7d)
    :return: 0.43553
    """
    try:
        start, end = format_exchange_start_and_end_times(params.exchange, params.timestamp, 1)
        interval = format_exchange_interval(params.exchange, params.interval)
        ex = EXCHANGE_ADAPTORS[params.exchange]()
        pair = format_exchange_pair(params.exchange, params.mkt_coin, params.base_coin)
        RATE_LIMITERS[params.exchange].limit()
        pair_rate = ex.get_historical_rate(pair=pair, start=start, end=end, interval=interval)
        return pair_rate
    except APIRequestError as e:
        log.error(e.error_msg)
        return None