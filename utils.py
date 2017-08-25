def is_valid_market(mkt_name, currencies):
    return mkt_name.split('-')[0] in currencies
