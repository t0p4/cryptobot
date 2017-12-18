from src.bot.crypto_bot import CryptoBot
from src.strats.bollinger_bands_strat import BollingerBandsStrat
from src.strats.stochastic_rsi_strat import StochasticRSIStrat
from src.strats.williams_pct_strat import WilliamsPctStrat
from src.strats.volume_strat import VolumeStrat
from src.exchange.exchange_factory import ExchangeFactory
import datetime
import os

BACKTESTING_START_DATE = datetime.datetime(2017, 1, 1)
BACKTESTING_END_DATE = datetime.datetime(2017, 8, 31)
BACKTESTING = os.getenv('BACKTESTING', 'FALSE')

if BACKTESTING == 'TRUE':
    btrx = ExchangeFactory().get_exchange()(BACKTESTING_START_DATE, BACKTESTING_END_DATE)
else:
    btrx = ExchangeFactory().get_exchange()()

MAJOR_TICK_SIZE = int(os.getenv('MAJOR_TICK_SIZE', 5))
SMA_WINDOW = 15
bb_options = {
    'name': 'BollingerBands',
    'active': True,
    'market_names': [],
    'plot_overlay': True,
    'num_standard_devs': 2,
    'sma_window': SMA_WINDOW,
    'sma_stat_key': 'last',
    'minor_tick': 1,
    'major_tick': MAJOR_TICK_SIZE
}
stoch_rsi_options = {
    'name': 'StochasticRSI',
    'active': True,
    'market_names': [],
    'plot_overlay': False,
    'rsi_window': SMA_WINDOW,
    'sma_window': 3,
    'stat_key': 'last',
    'minor_tick': 1,
    'major_tick': MAJOR_TICK_SIZE
}
w_pct_options = {
    'name': 'WilliamsPct',
    'active': True,
    'market_names': [],
    'plot_overlay': False,
    'stat_key': 'last',
    'wp_window': SMA_WINDOW,
    'minor_tick': 1,
    'major_tick': MAJOR_TICK_SIZE
}
vol_options = {
    'name': 'VolumeOSC',
    'active': True,
    'minor_tick': 1,
    'major_tick': MAJOR_TICK_SIZE,
    'pvo_ema_period': 9,
    'short_vol_ema_period': 12,
    'long_vol_ema_period': 26,
    'vol_roc_period': 3,
    'plot_overlay': False
}

strat1 = BollingerBandsStrat(bb_options)
strat2 = StochasticRSIStrat(stoch_rsi_options)
strat3 = WilliamsPctStrat(w_pct_options)
strat4 = VolumeStrat(vol_options)

bot = CryptoBot([strat4], btrx)

# bot.get_balance('ETH')
# bot.get_balances()
# bot.get_order_history('ETH-BCC', 50)
# bot.BUY_instant('ETH-NEO', 0.01)
# bot.BUY_market('ETH-NEO', 0.01)
# bot.sell_market('ETH-NEO', 0.01)
# bot.collect_summaries()
# bot.rate_limiter_start()
# bot.rate_limiter_limit()

# bot.get_historical_data()
bot.run()
# bot.calculate_num_coins('buy', 'BTC-ETH', 1)
# bot.send_report('This is a test', 'TEST REPORT')
