from src.bot.portfolio_reporter import PortfolioReporter
import datetime
import os

BACKTESTING_START_DATE = datetime.datetime(2017, 1, 1)
BACKTESTING_END_DATE = datetime.datetime(2017, 8, 31)
BACKTESTING = os.getenv('BACKTESTING', 'FALSE')

rep = PortfolioReporter(['gemini', 'gdax', 'binance', 'bittrex', 'gateio'])
rep.generate_p_report()
