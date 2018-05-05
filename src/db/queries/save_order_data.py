def save_order_data(trade_data, table_name):
    fmt_str = """(
        '{order_id}',
        '{exchange}',
        '{order_type}',
        '{pair}',
        '{base_coin}',
        '{mkt_coin}',
        '{trade_direction}',
        '{is_live}',
        '{is_cancelled}',
        {original_amount},
        {executed_amount},
        {remaining_amount},
        {price},
        {avg_price},
        {rate_btc},
        {rate_eth},
        {rate_usd},
        {cost_avg_btc},
        {cost_avg_eth},
        {cost_avg_usd},
        {analyzed},
        {timestamp},
        {save_time}
    )"""

    columns = """
        order_id,
        exchange,
        order_type,
        pair,
        base_coin,
        mkt_coin,
        side,
        is_live,
        is_cancelled,
        original_amount,
        executed_amount,
        remaining_amount,
        price,
        avg_price,
        rate_btc,
        rate_eth,
        rate_usd,
        cost_avg_btc,
        cost_avg_eth,
        cost_avg_usd,
        analyzed,
        timestamp,
        save_time
    """
    values = ','.join(fmt_str.format(**trade) for trade in trade_data)
    query = """ INSERT INTO """ + table_name + """ (%(columns)s) VALUES %(values)s ; """
    return query, columns, values