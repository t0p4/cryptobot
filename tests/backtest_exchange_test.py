from src.exchange.backtest_exchange import BacktestExchange
import datetime

TESTING_START_DATE = datetime.datetime(2017, 1, 1)
TESTING_END_DATE = datetime.datetime(2017, 8, 31)


class TestBacktestExchange:
    def setup_class(self):
        self.be = BacktestExchange(TESTING_START_DATE, TESTING_END_DATE)

    def teardown_class(self):
        self.be = None

    def test_buylimit(self):
        market = 'BTC-LTC'
        quantity = 2
        rate = 0.05
        trade_resp = self.be.buylimit(market, quantity, rate)
        assert(isinstance(trade_resp, dict))
        assert(isinstance(trade_resp['uuid'], float))
        assert(self.be.getbalance('BTC') == 19.9)
        assert(self.be.getbalance('LTC') == 2)

    def test_selllimit(self):
        self.be.balances['LTC'] = 10
        market = 'BTC-LTC'
        quantity = 5
        rate = 0.05
        trade_resp = self.be.selllimit(market, quantity, rate)
        assert (isinstance(trade_resp, dict))
        assert (isinstance(trade_resp['uuid'], float))
        assert (self.be.getbalance('BTC') == 20.15)
        assert (self.be.getbalance('LTC') == 5)
