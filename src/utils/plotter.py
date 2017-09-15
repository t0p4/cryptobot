import matplotlib.pyplot as plt
import pylab


class Plotter:
    def __init__(self):
        pass

    def plot_market(self, market):
        mkt_data = market[:]['last']
        plt.figure()
        mkt_data.plot()
        pylab.show()
