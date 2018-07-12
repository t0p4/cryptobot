from src.bot.crypto_bot import CryptoBot
from src.strats.bollinger_bands_strat import BollingerBandsStrat
from src.strats.stochastic_rsi_strat import StochasticRSIStrat
from src.strats.williams_pct_strat import WilliamsPctStrat
from src.strats.volume_strat import VolumeStrat
from src.strats.mkt_cap_index_strat import IndexStrat2
from src.strats.mkt_cap_ema_index_strat import EMAIndexStrat
from src.strats.macd_strat import MACDStrat
from src.exchange.exchange_factory import ExchangeFactory
from src.bot.portfolio_reporter import PortfolioReporter
from src.db.psql import PostgresConnection
from src.data_structures.historical_prices import HistoricalRates
from src.exchange.exchange_adaptor import ExchangeAdaptor
import datetime
import os
from src.utils.utils import merge_2_dicts
from src.exceptions import NoDataError

BACKTESTING_START_DATE = datetime.datetime(2017, 1, 1)
BACKTESTING_END_DATE = datetime.datetime(2017, 8, 31)
BACKTESTING = os.getenv('BACKTESTING', 'FALSE')


index_base_options = {
    'name': 'Basic Index',
    'active': True,
    'plot_overlay': False,
    'stat_key': 'market_cap',
    'window': 26,
    'ema_window': 90,
    'sma_window': 9,
    'index_depth': 25,
    'trade_threshold_pct': .0001,
    'blacklist': ['USDT', 'XVG'],
    'whitelist': None
}

## CRYPTO INDEX OPTIONS

cc20_options = {
    'name': 'CC20 (Chrisyviro Crypto Index)',
    'index_depth': 20
}
bitwise_options = {
    'name': 'Bitwise Index',
    'index_depth': 10,
    'whitelist': ['BTC', 'ETH', 'LTC', 'ETC', 'BCC', 'ZEC', 'DASH', 'XRP', 'XLM', 'XEM']
}
coinbase_options = {
    'name': 'Coinbase Index',
    'index_depth': 4,
    'whitelist': ['BTC', 'BCH', 'ETH', 'LTC', 'ETC']
}
bitcoin_options = {
    'name': 'Bitcoin',
    'index_depth': 1,
    'whitelist': ['BTC']
}

CC20 = merge_2_dicts(index_base_options, cc20_options)
Bitcoin = merge_2_dicts(index_base_options, bitcoin_options)
Coinbase = merge_2_dicts(index_base_options, coinbase_options)
Bitwise = merge_2_dicts(index_base_options, bitwise_options)

crypto_indexes = [CC20]

## STOCK INDEX OPTIONS

sp500_options = {
    'name': 'SP500',
    'index_depth': 1,
    'stat_key': 'close'
}
dji_options = {
    'name': 'DJI',
    'index_depth': 1,
    'stat_key': 'close'
}

SP500 = merge_2_dicts(index_base_options, sp500_options)
DJI = merge_2_dicts(index_base_options, dji_options)

stock_indexes = [SP500, DJI]

# EMA INDEX

ema_index = {
    'name': 'MC_EMA_DIFF',
    'index_depth': 20,
    'pre_index_depth': 40,
    'ema_window': 90,
    'sma_window': 30,
    'stat_key': 'market_cap',
    'weights': {
        'stat_weight': .8,
        'ema_diff_avg_weight': .2
    },
    'stat_top_percentile': .9
}

EMA = merge_2_dicts(index_base_options, ema_index)

# for i in range(90, 100):
#     try:
#         EMA['weights']['stat_weight'] = round(i / 100, 2)
#         EMA['weights']['ema_diff_avg_weight'] = round(1 - (i / 100), 2)
#         index_strat = EMAIndexStrat(EMA)
#         bot = CryptoBot({'v1_strats': [], 'index_strats': [index_strat]})
#         bot.run_cmc_ema_index_test()
#     except NoDataError:
#         continue

# for crypto_index in crypto_indexes:
#     try:
#         index_strat = IndexStrat2(crypto_index)
#         bot = CryptoBot({'v1_strats': [], 'index_strats': [index_strat]})
#         bot.run_cmc_index_test()
#     except NoDataError:
#         continue

# for stock_index in stock_indexes:
#     try:
#         index_strat = IndexStrat2(stock_index)
#         bot = CryptoBot({'v1_strats': [], 'index_strats': [index_strat]})
#         bot.run_stock_index_test()


# bot.load_stock_csv_into_db(['dji', 'sp500'])

rep = PortfolioReporter([])
rep.compare_indexes(index_id_list=['CC20 (Chrisyviro Crypto Index)', 'Coinbase Index', 'Bitcoin', 'DJI', 'MC_EMA_DIFF_0.9/0.1'])
