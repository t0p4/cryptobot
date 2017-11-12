from src.bot.crypto_bot import CryptoBot, MAJOR_TICK_SIZE
from src.strats.bollinger_bands_strat import BollingerBandsStrat
from src.exchange.exchange_factory import ExchangeFactory
import datetime

BACKTESTING_START_DATE = datetime.datetime(2017, 1, 1)
BACKTESTING_END_DATE = datetime.datetime(2017, 8, 31)
BACKTESTING = False

btrx = ExchangeFactory().get_exchange()()

SMA_WINDOW = 20
bb_options = {
    'active': True,
    'market_names': [],
    'num_standard_devs': 2,
    'sma_window': SMA_WINDOW,
    'sma_stat_key': 'last',
    'minor_tick': 1,
    'major_tick': MAJOR_TICK_SIZE
}

strat = BollingerBandsStrat(bb_options)

bot = CryptoBot([strat], btrx)

bot.collect_currencies()
bot.collect_markets()
bot.collect_summaries()
