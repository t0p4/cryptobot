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

        fig, plots = plt.subplots(1 + num_non_overlayed_indicators, 1, sharex=True)
        plots[0].set_title(mkt_name)
        plots[0].set_xlabel('Time')
        plots[0].set_ylabel('Rate')
        plots[0].axes.axes.xaxis.major.formatter = self.date_formatter
        plots[0].plot_date(buy_times, buys, color='green', marker='^')
        plots[0].plot_date(sell_times, sells, color='red', marker='v')
        plots[0].plot(time_series, price_series)

        # self.plot_bb(mkt_data, time_series, plots[0])
        # self.plot_stochastic_rsi(mkt_data, time_series, plots[1])

        non_overlayed_indicator_idx = 0
        for strat in strats:
            subplot = 0
            if not strat.plot_overlay:
                non_overlayed_indicator_idx += 1
                subplot += non_overlayed_indicator_idx
            self.strat_plotters[strat.name](mkt_data, time_series, plots[subplot])
        pylab.show()

    def plot_stochastic_rsi(self, mkt_data, time_series, subplot):
        subplot.set_xlabel('Time')
        subplot.set_ylabel('Stochastic RSI')
        subplot.axes.axes.xaxis.major.formatter = self.date_formatter
        stoch_rsi = mkt_data[:]['STOCH_RSI']
        stoch_rsi_sma = mkt_data[:]['STOCH_RSI_SMA']
        subplot.plot(time_series, stoch_rsi)
        subplot.plot(time_series, stoch_rsi_sma)

    def plot_bb(self, mkt_data, time_series, subplot):
        sma = mkt_data[:]['SMA']
        upper_bb = mkt_data[:]['UPPER_BB']
        lower_bb = mkt_data[:]['LOWER_BB']
        subplot.plot(time_series, sma)
        subplot.plot(time_series, upper_bb)
        subplot.plot(time_series, lower_bb)

    def plot_w_pct(self, mkt_data, time_series, subplot):
        subplot.set_ylabel('Williams %')