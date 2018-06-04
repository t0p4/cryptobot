def save_index_balances(index_balances, table_name):
    fmt_str = """(
        '{coin}',
        '{id}',
        {balance},
        {balance_usd},
        {index_pct},
        '{index_date}'
    )"""
    columns = """
        coin,
        id,
        balance,
        balance_usd,
        index_pct,
        index_date
    """
    values = ','.join(fmt_str.format(**asset) for idx, asset in index_balances.iterrows())
    query = """ INSERT INTO """ + table_name + """ (%(columns)s) VALUES %(values)s ; """
    return query, columns, values
