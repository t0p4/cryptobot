
def convert_to_base_value(amt, rate):
    return amt * rate


def convert_rates(coin1_coin2_rate, coin_2_coin3_rate):
    coin1_coin3_rate = coin1_coin2_rate * coin_2_coin3_rate
    return coin1_coin3_rate


def get_usd_value(num_coins, coin_rates, exchange_rates):
    """
        calculates the usd value for a given coin
    :param num_coins: 8000
    :param coin_rates: {"ETH": 0.048, "BTC": 0.0094}
    :param exchange_rates: {"ETH": 1050, "BTC": 11070}  [in USD]
    :return: 15467.445, btc, gemini
    """
    usd_rate, base_coin = get_usd_rate(coin_rates, exchange_rates)
    usd_value = convert_to_base_value(num_coins, usd_rate)
    return usd_value, base_coin


def get_usd_rate(coin_rates, usd_rates):
    """
        calculates the usd rate for a given coin, based on the max of trading it on gemini or gdax

        ex. AION_ETH * ETH_USD = AION_USD

    :param coin_rates: {"ETH": 0.048, "BTC": 0.0094}
    :param usd_rates: {"ETH": 1050, "BTC": 11070}
    :return: 475, btc, gemini
    """

    current_max = 0
    current_max_coin = ''

    for coin, rate in coin_rates.items():
        current_val = rate * usd_rates[coin.upper()]
        if current_val > current_max:
            current_max = current_val
            current_max_coin = coin

    return current_max, current_max_coin


def calculate_cost_average(prev_num_coins, prev_coin_price, num_new_coins, new_coin_price):
    total_coins = prev_num_coins + num_new_coins
    return (prev_num_coins * prev_coin_price + num_new_coins * new_coin_price) / total_coins


def convert_str_columns_to_num(df, keys):
    for key in keys:
        df[key] = df[key].apply(lambda x: float(x))
    return df
