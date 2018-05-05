def save_tickers(tickers, table_name):
    fmt_str = """(
        '{pair}',
        '{base_coin}',
        '{mkt_coin}',
        {open},
        {high},
        {low},
        {close},
        {bid},
        {ask},
        {last},
        {vol_base},
        {vol_mkt},
        {timestamp},
        '{exchange}',
        {ticker_nonce}
    )"""
    columns = """
        pair,
        base_coin,
        mkt_coin,
        open,
        high,
        low,
        close,
        bid,
        ask,
        last,
        vol_base,
        vol_mkt,
        timestamp,
        exchange,
        ticker_nonce
    """
    values = ','.join(fmt_str.format(**ticker) for ticker in tickers)
    query = """ INSERT INTO """ + table_name + """ (%(columns)s) VALUES %(values)s ; """
    return query, columns, values
