from src.exchange.backtest_exchange import BacktestExchange
import datetime

BACKTESTING_START_DATE = datetime.datetime(2017, 1, 1)
BACKTESTING_END_DATE = datetime.datetime(2017, 8, 31)


class TestBacktestExchange:
    def setup_class(self):
        self.be = BacktestExchange(BACKTESTING_START_DATE, BACKTESTING_END_DATE)

    def teardown_class(self):
        self.be = None

    def test_buylimit(self):
        market = 'BTC-LTC'
        quantity = 2
        rate = 0.05
        trade_resp = self.be.buylimit(market, quantity, rate)
        assert(isinstance(trade_resp, dict))
        assert(isinstance(trade_resp['uuid'], float))
        assert(self.be.getbalance('BTC')['balance'] == 19.9)
        assert(self.be.getbalance('LTC')['balance'] == 2)

    def test_selllimit(self):
        self.be.balances['LTC']['balance'] = 10
        market = 'BTC-LTC'
        quantity = 5
        rate = 0.05
        trade_resp = self.be.selllimit(market, quantity, rate)
        assert (isinstance(trade_resp, dict))
        assert (isinstance(trade_resp['uuid'], float))
        assert (self.be.getbalance('BTC')['balance'] == 20.15)
        assert (self.be.getbalance('LTC')['balance'] == 5)

    def test_getorderbook_buy(self):
        market = 'BTC-LTC'
        order_type = 'buy'
        depth = 20
        market_summaries = self.be.getmarketsummaries()
        btc_ltc_summary = next(summary for summary in market_summaries if summary['marketname'] == market)
        order_book = self.be.getorderbook(market, order_type, depth)
        assert(len(order_book['buy']) == 1)
        assert('sell' not in order_book)
        assert(order_book['buy'][0]['Quantity'] == 999999999)
        assert(order_book['buy'][0]['Rate'] == btc_ltc_summary['bid'])

    def test_getorderbook_sell(self):
        market = 'BTC-LTC'
        order_type = 'sell'
        depth = 20
        market_summaries = self.be.getmarketsummaries()
        btc_ltc_summary = next(summary for summary in market_summaries if summary['marketname'] == market)
        order_book = self.be.getorderbook(market, order_type, depth)
        assert(len(order_book['sell']) == 1)
        assert ('buy' not in order_book)
        assert(order_book['sell'][0]['Quantity'] == 999999999)
        assert(order_book['sell'][0]['Rate'] == btc_ltc_summary['ask'])

    def test_getorderbook_both(self):
        market = 'BTC-LTC'
        order_type = 'both'
        depth = 20
        market_summaries = self.be.getmarketsummaries()
        btc_ltc_summary = next(summary for summary in market_summaries if summary['marketname'] == market)
        order_book = self.be.getorderbook(market, order_type, depth)
        assert(len(order_book['buy']) == 1)
        assert(order_book['buy'][0]['Quantity'] == 999999999)
        assert(order_book['buy'][0]['Rate'] == btc_ltc_summary['bid'])
        assert(len(order_book['sell']) == 1)
        assert(order_book['sell'][0]['Quantity'] == 999999999)
        assert(order_book['sell'][0]['Rate'] == btc_ltc_summary['ask'])

    def test_getticker(self):
        market = 'BTC-LTC'
        market_summaries = self.be.getmarketsummaries()
        btc_ltc_summary = next(summary for summary in market_summaries if summary['marketname'] == market)
        ticker = self.be.getticker(market)
        assert(ticker['Bid'] == btc_ltc_summary['bid'])
        assert(ticker['Ask'] == btc_ltc_summary['ask'])
        assert(ticker['Last'] == btc_ltc_summary['last'])