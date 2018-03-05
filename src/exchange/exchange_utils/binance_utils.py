import time


def create_normalized_trade_data_binance(trade_data, pair_meta_data, trade_dir, rates):
    return {
        'order_type': 'limit',
        'base_currency': pair_meta_data['base_coin'],
        'market_currency': pair_meta_data['mkt_coin'],
        'quantity': trade_data['qty'],
        'rate': trade_data['price'],
        'trade_id': trade_data['orderId'],
        'exchange_id': 'binance',
        'trade_time': trade_data['time'],
        'save_time': time.time(),
        'rate_btc': rates['btc'],
        'rate_eth': rates['eth'],
        'rate_usd': rates['usd'],
        'trade_direction': trade_dir,
        'cost_avg_btc': 0,
        'cost_avg_eth': 0,
        'cost_avg_usd': 0,
        'analyzed': False
    }


def create_normalized_exchange_pairs_binance(exchange_pair_data):
    return [{'pair': ex['symbol'], 'base_coin': ex['baseAsset'], 'mkt_coin': ex['quoteAsset']} for ex in
            exchange_pair_data['symbols']]
