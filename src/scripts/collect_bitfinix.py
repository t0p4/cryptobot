from src.bot.crypto_bot import CryptoBot
bot = CryptoBot({'v1_strats': [], 'index_strats': []})
bot.collect_historical_tickers('bitfinex')
