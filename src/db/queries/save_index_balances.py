def save_index_balances(index_balances, table_name):
    fmt_str = """(
        '{coin}',
        '{id}',
        '{index_id}',
        {balance},
        {balance_usd},
        {index_pct},
        '{index_date}'
    )"""
    columns = """
        coin,
        id,
        index_id,
        balance,
        balance_usd,
        index_pct,
        index_date
    """
    values = ','.join(fmt_str.format(**asset) for idx, asset in index_balances.iterrows())
    query = """ INSERT INTO """ + table_name + """ (%(columns)s) VALUES %(values)s ; """
    return query, columns, values


def save_index_metadata(index_metadata, table_name):
    fmt_str = """(
        '{index_id}',
        '{index_date}',
        {portfolio_balance_usd},
        {bitcoin_value_usd}
    )"""
    columns = """
        index_id,
        index_date,
        portfolio_balance_usd,
        bitcoin_value_usd
    """
    values = fmt_str.format(**index_metadata)
    query = """ INSERT INTO """ + table_name + """ (%(columns)s) VALUES %(values)s ; """
    return query, columns, values