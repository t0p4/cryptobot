from src.exceptions import InvalidCoinError
from src.utils.utils_algos import binary_search, binary_insert


class HistoricalRates:
    def __init__(self):
        self.sorted_timestamps_by_base_coin = {}
        # {
        #     "BTC": [122394859589, 12245554658978, ...],   // sorted
        #     "ETH": [122394859589, 12245554658978, ...]    // sorted
        # }

        self.rates_by_timestamp_by_base_coin = {}
        # {
        #     "BTC": {
        #         122394859589: {"ETH": .13, "USD": .0003},
        #         12245554658978: {"ETH": .14, "USD": .0005}
        #         ...
        #     },
        #     "BTC": {
        #         122394859589: {"BTC": 10.23, "USD": .0029},
        #         12245554658978: {"BTC": 10.4, "USD": .0032}
        #         ...
        #     }
        # }

    def get_rate(self, timestamp, base_coin, market_coin=None):
        try:
            found, held_timestamp = binary_search(timestamp, self.sorted_timestamps_by_base_coin[base_coin])
            if found:
                rate = self.rates_by_timestamp_by_base_coin[base_coin][held_timestamp]
                if market_coin is not None and market_coin in rate:
                    return found, rate[market_coin]
                else:
                    return found, rate
            else:
                return found, None
        except Exception:
            raise InvalidCoinError(base_coin)

    def add_rate(self, timestamp, base_coin, rate_data):
        try:
            binary_insert(timestamp, self.sorted_timestamps_by_base_coin[base_coin])
            if timestamp in self.rates_by_timestamp_by_base_coin:
                rates_by_base_coin = self.rates_by_timestamp_by_base_coin[timestamp]
                if base_coin in rates_by_base_coin:
                    self.rates_by_timestamp_by_base_coin[timestamp][base_coin] = {**rates_by_base_coin[base_coin], **rate_data}
                else:
                    self.rates_by_timestamp_by_base_coin[timestamp][base_coin] = rate_data
            else:
                self.rates_by_timestamp_by_base_coin[timestamp] = {base_coin: rate_data}
                return
        except Exception:
            raise InvalidCoinError(base_coin)
