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
        x2 = trades[:]['timestamp']
        buys = trades[:]['rate']
        plt.figure()
        # plt.gcf().axes[0].xaxis.set_major_formatter(self.date_formatter)
        plt.axes().xaxis.set_major_formatter(self.date_formatter)
        plt.title(mkt_name)
        plt.xlabel('Time')
        plt.ylabel('Rate')
        plt.plot(x1, y1)
        plt.plot_date(x2, buys)
        pylab.show()
