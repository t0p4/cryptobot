from src.exceptions import InvalidCoinError
from src.utils.utils_algos import binary_search, binary_insert
from collections import defaultdict


class HistoricalRates:
    def __init__(self, exchange):
        self.sorted_timestamps_by_base_coin = defaultdict(list)
        # {
        #     "BTC": [122394859589, 12245554658978, ...],   // sorted
        #     "ETH": [122394859589, 12245554658978, ...]    // sorted
        # }

        self.rates_by_timestamp_by_base_coin = defaultdict(dict)
        # {
        #     "BTC": {
        #         122394859589: {"ETH": .13, "USD": .0003},
        #         122455546588: {"ETH": .14, "USD": .0005}
        #         ...
        #     },
        #     "ETH": {
        #         122394859589: {"BTC": 10.23, "USD": .0029},
        #         122455546588: {"BTC": 10.41, "USD": .0032}
        #         ...
        #     }
        # }
        self.exchange = exchange

    def get_rate(self, timestamp, base_coin, mkt_coin=None):
        b_c = base_coin.upper()
        m_c = mkt_coin.upper()
        try:
            if b_c in self.sorted_timestamps_by_base_coin:
                found, held_timestamp, _ = binary_search(timestamp, self.sorted_timestamps_by_base_coin[b_c])
                if found:
                    rate = self.rates_by_timestamp_by_base_coin[held_timestamp][b_c]
                    if m_c is not None and m_c in rate:
                        return found, rate[m_c]
                    else:
                        return False, None
            return False, None
        except Exception as e:
            raise InvalidCoinError(base_coin, self.exchange)

    def add_rate(self, timestamp, base_coin, rate_data):
        b_c = base_coin.upper()
        try:
            self.sorted_timestamps_by_base_coin[b_c] = binary_insert(timestamp, self.sorted_timestamps_by_base_coin[b_c])
            if timestamp in self.rates_by_timestamp_by_base_coin:
                rates_by_base_coin = self.rates_by_timestamp_by_base_coin[timestamp]
                if b_c in rates_by_base_coin:
                    self.rates_by_timestamp_by_base_coin[timestamp][b_c] = {**rates_by_base_coin[b_c], **rate_data}
                else:
                    self.rates_by_timestamp_by_base_coin[timestamp][b_c] = rate_data
            else:
                self.rates_by_timestamp_by_base_coin[timestamp] = {b_c: rate_data}
                return
        except Exception as e:
            print(e)
            raise InvalidCoinError(b_c, self.exchange)
