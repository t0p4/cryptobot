def save_trade_data(trade_data, table_name):
    fmt_str = """(
        '{order_type}',
        '{trade_id}',
        '{exchange_id}',
        '{quantity}',
        '{pair}',
        '{base_coin}',
        '{mkt_coin}',
        '{trade_direction}',
        {rate},
        {rate_btc},
        {rate_eth},
        {rate_usd},
        {cost_avg_btc},
        {cost_avg_eth},
        {cost_avg_usd},
        {analyzed},
        {trade_time}
    )
    """

    columns = """
        order_type,
        trade_id,
        exchange_id,
        quantity,
        pair,
        base_coin,
        mkt_coin,
        trade_direction,
        rate,
        rate_btc,
        rate_eth,
        rate_usd,
        cost_avg_btc,
        cost_avg_eth,
        cost_avg_usd,
        analyzed,
        trade_time
    """
    values = ','.join(fmt_str.format(**trade) for trade in trade_data)
    query = """ INSERT INTO """ + table_name + """ (%(columns)s) VALUES %(values)s ; """
    return query, columns, values