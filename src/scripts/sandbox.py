from src.bot.crypto_bot import CryptoBot
from src.strats.bollinger_bands_strat import BollingerBandsStrat
from src.strats.stochastic_rsi_strat import StochasticRSIStrat
from src.strats.williams_pct_strat import WilliamsPctStrat
from src.strats.volume_strat import VolumeStrat
from src.strats.macd_strat import MACDStrat
from src.exchange.exchange_factory import ExchangeFactory
from src.bot.portfolio_reporter import PortfolioReporter
from src.db.psql import PostgresConnection
from src.data_structures.historical_prices import HistoricalRates
from src.exchange.exchange_adaptor import ExchangeAdaptor
import datetime
import os

BACKTESTING_START_DATE = datetime.datetime(2017, 1, 1)
BACKTESTING_END_DATE = datetime.datetime(2017, 8, 31)
BACKTESTING = os.getenv('BACKTESTING', 'FALSE')

if BACKTESTING == 'TRUE':
    btrx = ExchangeFactory().get_exchange()(BACKTESTING_START_DATE, BACKTESTING_END_DATE)
else:
    btrx = ExchangeFactory().get_exchange()()

# MAJOR_TICK_SIZE = int(os.getenv('MAJOR_TICK_SIZE', 5))
# SMA_WINDOW = int(os.getenv('SMA_WINDOW', 15))
# bb_options = {
#     'name': 'BollingerBands',
#     'active': True,
#     'plot_overlay': True,
#     'stat_key': 'last',
#     'window': SMA_WINDOW,
#     'sma_window': SMA_WINDOW,
#     'num_standard_devs': 2,
# }
# stoch_rsi_options = {
#     'name': 'StochasticRSI',
#     'active': True,
#     'plot_overlay': False,
#     'stat_key': 'last',
#     'window': SMA_WINDOW,
#     'sma_window': 3,
#     'rsi_window': SMA_WINDOW,
# }
# w_pct_options = {
#     'name': 'WilliamsPct',
#     'active': True,
#     'plot_overlay': False,
#     'stat_key': 'last',
#     'window': SMA_WINDOW,
#     'wp_window': SMA_WINDOW,
# }
# vol_options = {
#     'name': 'VolumeOSC',
#     'active': True,
#     'plot_overlay': False,
#     'stat_key': 'volume',
#     'window': 26,
#     'pvo_ema_window': 9,
#     'short_vol_ema_window': 12,
#     'long_vol_ema_window': 26,
#     'vol_roc_window': 3,
# }
# macd_options = {
#     'name': 'MACD',
#     'active': True,
#     'plot_overlay': False,
#     'stat_key': 'last',
#     'window': 26,
#     'slow_ema_window': 26,
#     'fast_ema_window': 12,
#     'sma_window': 9
# }
#
# bb_strat = BollingerBandsStrat(bb_options)
# stoch_rsi_strat = StochasticRSIStrat(stoch_rsi_options)
# w_pct_strat = WilliamsPctStrat(w_pct_options)
# vol_strat = VolumeStrat(vol_options)
# macd_strat = MACDStrat(macd_options)
#
# bot = CryptoBot([macd_strat], btrx)

# bot.get_balance('ETH')
# bot.get_balances()
# bot.get_order_history('ETH-BCC', 50)
# bot.BUY_instant('ETH-NEO', 0.01)
# bot.BUY_market('ETH-NEO', 0.01)
# bot.sell_market('ETH-NEO', 0.01)

# bot.rate_limiter_start()
# bot.rate_limiter_limit()

# bot.collect_markets()
# bot.collect_currencies()
# bot.collect_summaries()

# bot.get_historical_data()
# bot.run()
# bot.calculate_num_coins('buy', 'BTC-ETH', 1)
# bot.send_report('This is a test', 'TEST REPORT')







# rep = PortfolioReporter(['binance', 'bittrex', 'gemini'])
# rep.generate_p_report()
# rep.pull_all_trade_data_from_exchanges()






#
# EXCHANGES = [
#     # 'binance',
#     # 'bittrex',
#     'gemini'
# ]
#
# historical_rates = HistoricalRates()
# ex_ad = ExchangeAdaptor(historical_rates)
# for ex in EXCHANGES:
#     # bals = ex_ad.get_account_balances(ex)
#     # print(repr(bals))
#     pairs = ex_ad.get_exchange_pairs(ex)
#     trades_by_pair = {}
#     for pair in pairs:
#         # trades = ex_ad.get_historical_trades(ex, pair=pair)
#         ticker = ex_ad.get_current_pair_ticker(ex, pair)
#     print(ex)

balances = ExchangeAdaptor().get_historical_trades('cryptopia', {'pair': 'DOT/BTC', 'base_coin': 'BTC', 'mkt_coin': 'DOT'})
print('ok')
# balances2 = ExchangeAdaptor().get_current_tickers('gdax', False)
# print('ok')