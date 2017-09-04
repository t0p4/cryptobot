from src.strats.base_strat import BaseStrategy
import pandas as pd


class BollingerBandsStrat(BaseStrategy):
    def __init__(self, options):
        BaseStrategy.__init__(self, options)