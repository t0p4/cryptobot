from datetime import datetime

UNIT_MAPPINGS = {
    's': 1000,
    'm': 60000,
    'h': 3600000,
    'd': 86400000,
    'w': 604800000
}

def format_exchange_pair(exchange, mkt_coin, base_coin):
    if exchange == 'binance':
        return mkt_coin.upper() + base_coin.upper()
    elif exchange == 'gdax_public':
        return mkt_coin.upper() + '-' + base_coin.upper()


def format_exchange_start_and_end_times(exchange, timestamp, minutes):
    divisor = 1
    if exchange == 'binance':
        divisor = 1
    elif exchange == 'gdax_public':
        divisor = 1000

    start = datetime.fromtimestamp(timestamp / divisor).isoformat()
    end = datetime.fromtimestamp(timestamp / divisor + (minutes * 60000 / divisor)).isoformat()
    return start, end


def format_exchange_interval(exchange, interval):
    if exchange == 'binance':
        return interval
    elif exchange == 'gdax_public':
        count = interval[0]
        unit = interval[1]
        return count * unit / 1000
