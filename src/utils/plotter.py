import matplotlib.pyplot as plt
import pylab
from matplotlib.dates import DateFormatter


class Plotter:
    def __init__(self):
        self.date_formatter = DateFormatter('%H:%M')
        self.strat_plotters = {
            'BollingerBands': self.plot_bb,
            'StochasticRSI': self.plot_stochastic_rsi,
            'WilliamsPct': self.plot_w_pct,
            'VolumeOSC': self.plot_vol_osc,
            'MACD': self.plot_macd
        }
        self.num_non_overlayed_indicators = 0
        self.plots = {}
        pass

    def get_plot(self, idx):
        if self.num_non_overlayed_indicators > 0:
            return self.plots[idx]
        else:
            return self.plots

    def plot_market(self, mkt_name, mkt_data, trades, strats, save_plot=False, show_plot=True):
        time_series = mkt_data[:]['saved_timestamp']
        price_series = mkt_data[:]['last']

        self.num_non_overlayed_indicators = 0
        for strat in strats:
            if not strat.plot_overlay:
                self.num_non_overlayed_indicators += 1

        fig, plots = plt.subplots(1 + self.num_non_overlayed_indicators, sharex=True)
        self.plots = plots
        self.get_plot(0).set_title(mkt_name)
        self.get_plot(0).set_xlabel('Time')
        self.get_plot(0).set_ylabel('Rate')
        self.get_plot(0).plot(time_series, price_series)
        self.get_plot(0).axes.xaxis.major.formatter = self.date_formatter

        if not trades.empty:
            buy_times = trades[trades['order_type'] == 'buy'][:]['timestamp']
            sell_times = trades[trades['order_type'] == 'sell'][:]['timestamp']
            buys = trades[trades['order_type'] == 'buy'][:]['rate']
            sells = trades[trades['order_type'] == 'sell'][:]['rate']
            self.get_plot(0).plot_date(buy_times, buys, color='green', marker='^')
            self.get_plot(0).plot_date(sell_times, sells, color='red', marker='v')

        # self.plot_bb(mkt_data, time_series, plots[0])
        # self.plot_stochastic_rsi(mkt_data, time_series, plots[1])

        non_overlayed_indicator_idx = 0
        for strat in strats:
            subplot = 0
            if not strat.plot_overlay:
                non_overlayed_indicator_idx += 1
                subplot += non_overlayed_indicator_idx
            self.strat_plotters[strat.name](mkt_data, time_series, self.get_plot(subplot))

        if show_plot:
            pylab.show()
        if save_plot:
            file_path = 'src/plots/'
            file_ext = '.png'
            fig.savefig(file_path + mkt_name + file_ext)
            plot_file_meta_data = {'file_path': file_path, 'file_name': mkt_name, 'file_ext': file_ext}
            return plot_file_meta_data

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
        subplot.set_xlabel('Time')
        subplot.set_ylabel('Williams %')
        subplot.axes.axes.xaxis.major.formatter = self.date_formatter
        w_pct = mkt_data[:]['W_PCT']
        subplot.plot(time_series, w_pct)

    def plot_vol_osc(self, mkt_data, time_series, subplot):
        subplot.set_xlabel('Time')
        subplot.set_ylabel('Volume OSC')
        subplot.axes.axes.xaxis.major.formatter = self.date_formatter
        pvo = mkt_data[:]['PVO']
        pvo_ema = mkt_data[:]['PVO_EMA']
        # volume = mkt_data[:]['volume']
        subplot.plot(time_series, pvo)
        subplot.plot(time_series, pvo_ema)
        # subplot.bar(time_series, volume)

    def plot_macd(self, mkt_data, time_series, subplot):
        subplot.set_xlabel('Time')
        subplot.set_ylabel('MACD')
        subplot.axes.axes.xaxis.major.formatter = self.date_formatter
        macd = mkt_data[:]['MACD']
        macd_sign = mkt_data[:]['MACD_sign']
        subplot.plot(time_series, macd)
        subplot.plot(time_series, macd_sign)