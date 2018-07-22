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
from src.utils.utils import merge_2_dicts, create_calendar_list
from src.exceptions import NoDataError

BACKTESTING_START_DATE = datetime.datetime(2017, 1, 1)
BACKTESTING_END_DATE = datetime.datetime(2017, 8, 31)
BACKTESTING = os.getenv('BACKTESTING', 'FALSE')

rep = PortfolioReporter([])
# index_id_list=['CC20 (Chrisyviro Crypto Index)', 'Coinbase Index', 'Bitcoin', 'DJI', 'MC_EMA_DIFF_0.95/0.05']
index_list = ['CC20 (Chrisyviro Crypto Index)', 'Bitcoin', 'DJI']
# for i in range(95, 100):
#     j = 100 - i
#     if i > 90:
#         j = '0' + str(j)
#     index_list.append('MC_EMA_DIFF_0.%s/0.%s' % (str(i), str(j)))
rep.compare_indexes(index_id_list=index_list)
