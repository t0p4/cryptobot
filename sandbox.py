from crypto_bot import CryptoBot

bot = CryptoBot()

# bot.get_balance('ETH')
# bot.get_balances()
# bot.get_order_history('ETH-BCC', 50)
# bot.BUY_instant('ETH-NEO', 0.01)
# bot.BUY_market('ETH-NEO', 0.01)
bot.SELL_market('ETH-NEO', 0.01)