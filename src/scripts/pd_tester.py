import pandas as pd

data = [
    {'bid': 10, 'last': 10, 'ask': 9, 'marketname': 'BTC-LTC', 'saved_timestamp': 0, 'volume': 1000},
    {'bid': 11, 'last': 10, 'ask': 10, 'marketname': 'BTC-LTC', 'saved_timestamp': 1, 'volume': 1100},
    {'bid': 10, 'last': 11, 'ask': 9, 'marketname': 'BTC-LTC', 'saved_timestamp': 2, 'volume': 1150},
    {'bid': 11, 'last': 10, 'ask': 8, 'marketname': 'BTC-LTC', 'saved_timestamp': 3, 'volume': 1200},
    {'bid': 10, 'last': 12, 'ask': 9, 'marketname': 'BTC-LTC', 'saved_timestamp': 4, 'volume': 1500}
]
df = pd.DataFrame(data)
tail = df.tail(5).reset_index(drop=True)
aggs = {'bid': ['last'], 'last': ['last'], 'ask': ['last'], 'marketname': ['last'], 'saved_timestamp': ['last'], 'volume': ['sum']}
tail = tail.groupby(tail.index / 5).agg(aggs)
print('done')