from src.bot.crypto_bot import CryptoBot
from src.strats.bollinger_bands_strat import BollingerBandsStrat

if TESTING:
    self.btrx = ExchangeFactory().get_exchange(TESTING)(TESTING_START_DATE, TESTING_END_DATE)
else:
    self.btrx = ExchangeFactory().get_exchange(TESTING)(BITTREX_API_KEY, BITTREX_API_SECRET)

bot = CryptoBot(BollingerBandsStrat)

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
