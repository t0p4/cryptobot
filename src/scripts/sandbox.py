from src.bot.crypto_bot import CryptoBot, MAJOR_TICK_SIZE
from src.strats.bollinger_bands_strat import BollingerBandsStrat
from src.exchange.exchange_factory import ExchangeFactory
from secrets import BITTREX_API_KEY, BITTREX_API_SECRET
import datetime

TESTING_START_DATE = datetime.datetime(2017, 1, 1)
TESTING_END_DATE = datetime.datetime(2017, 8, 31)
TESTING = False

if TESTING:
    btrx = ExchangeFactory().get_exchange(TESTING)(TESTING_START_DATE, TESTING_END_DATE)
else:
    btrx = ExchangeFactory().get_exchange(TESTING)(BITTREX_API_KEY, BITTREX_API_SECRET)

SMA_WINDOW = 20
bb_options = {
    'active': True,
    'market_names': [],
    'num_standard_devs': 2,
    'sma_window': SMA_WINDOW,
    'sma_stat_key': 'close',
    'minor_tick': 1,
    'major_tick': MAJOR_TICK_SIZE,
    'testing': TESTING
}

strat = BollingerBandsStrat(bb_options)

bot = CryptoBot(strat, btrx)

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
# bot.run()
