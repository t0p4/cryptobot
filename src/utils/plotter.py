import matplotlib.pyplot as plt
import pylab
from matplotlib.dates import DateFormatter


class Plotter:
    def __init__(self):
        self.date_formatter = DateFormatter('%H:%M')
        self.strat_plotters = {
            'BollingerBands': self.plot_bb,
            'StochasticRSI': self.plot_stochastic_rsi,
            'WilliamsPct': self.plot_w_pct
        }
        pass

    def plot_market(self, mkt_name, mkt_data, trades, strats):
        time_series = mkt_data[:]['saved_timestamp']
        price_series = mkt_data[:]['last']
        buy_times = trades[trades['order_type'] == 'buy'][:]['timestamp']
        sell_times = trades[trades['order_type'] == 'sell'][:]['timestamp']
        buys = trades[trades['order_type'] == 'buy'][:]['rate']
        sells = trades[trades['order_type'] == 'sell'][:]['rate']

        num_non_overlayed_indicators = 0
        for strat in strats:
            if not strat.plot_overlay:
                num_non_overlayed_indicators += 1

        rate_subplot = (num_non_overlayed_indicators + 1) * 100 + 11
        non_overlayed_indicator_idx = 0
        subplot = rate_subplot

        plt.figure()
        plt.title(mkt_name)
        plt.subplot(subplot)
        plt.xlabel('Time')
        plt.plot(time_series, price_series)
        plt.plot_date(buy_times, buys, color='green', marker='+')
        plt.plot_date(sell_times, sells, color='red', marker='+')
        plt.axes().xaxis.set_major_formatter(self.date_formatter)

        for strat in strats:
            subplot = rate_subplot
            if not strat.plot_overlay:
                non_overlayed_indicator_idx += 1
                subplot += non_overlayed_indicator_idx
            print(subplot)
            self.strat_plotters[strat.name](mkt_data, time_series, subplot)
        pylab.show()

    def plot_stochastic_rsi(self, mkt_data, time_series, subplot):
        plt.subplot(subplot)
        plt.ylabel('Stochastic RSI')
        stoch_rsi = mkt_data[:]['STOCH_RSI']
        stoch_rsi_sma = mkt_data[:]['STOCH_RSI_SMA']
        plt.plot(time_series, stoch_rsi)
        plt.plot(time_series, stoch_rsi_sma)

    def plot_bb(self, mkt_data, time_series, subplot):
        plt.subplot(subplot)
        sma = mkt_data[:]['SMA']
        upper_bb = mkt_data[:]['UPPER_BB']
        lower_bb = mkt_data[:]['LOWER_BB']
        plt.plot(time_series, sma)
        plt.plot(time_series, upper_bb)
        plt.plot(time_series, lower_bb)

    def plot_w_pct(self, mkt_data, time_series, subplot):
        plt.subplot(subplot)
        plt.ylabel('Williams %')