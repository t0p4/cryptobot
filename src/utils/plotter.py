import matplotlib.pyplot as plt
import pylab
from matplotlib.dates import DateFormatter


class Plotter:
    def __init__(self):
        self.date_formatter = DateFormatter('%H:%M')
        pass

    def plot_market(self, mkt_name, mkt_data, trades):
        x1 = mkt_data[:]['saved_timestamp']
        y1 = mkt_data[:]['last']
        buy_times = trades[trades['order_type'] == 'buy'][:]['timestamp']
        sell_times = trades[trades['order_type'] == 'sell'][:]['timestamp']
        buys = trades[trades['order_type'] == 'buy'][:]['rate']
        sells = trades[trades['order_type'] == 'sell'][:]['rate']
        sma = mkt_data[:]['SMA']
        upper_bb = mkt_data[:]['UPPER_BB']
        lower_bb = mkt_data[:]['LOWER_BB']
        plt.figure()
        plt.axes().xaxis.set_major_formatter(self.date_formatter)
        plt.title(mkt_name)
        plt.xlabel('Time')
        plt.ylabel('Rate')
        plt.plot(x1, y1)
        plt.plot_date(buy_times, buys, color='green', marker='+')
        plt.plot_date(sell_times, sells, color='red', marker='+')
        plt.plot(x1, sma)
        plt.plot(x1, upper_bb)
        plt.plot(x1, lower_bb)
        pylab.show()