import pandas
MARKET_SUMMARIES_FIXTURE = pandas.DataFrame([
    {'ask': 0.015600, 'basevolume': 3102.100000, 'bid': 0.015450, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015440, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2050.0, 'opensellorders': 5750.0, 'prevday': 0.017350, 'timestamp': '2017-09-04T16:56:39.717', 'volume': 191514.111111},
    {'ask': 0.015500, 'basevolume': 3102.258469, 'bid': 0.015440, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015445, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2057.0, 'opensellorders': 5755.0, 'prevday': 0.017300, 'timestamp': '2017-09-04T16:56:39.717', 'volume': 191513.554444},
    {'ask': 0.015500, 'basevolume': 3103.384469, 'bid': 0.015445, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015445, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2060.0, 'opensellorders': 5754.0, 'prevday': 0.017298, 'timestamp': '2017-09-04T16:57:16.597', 'volume': 191586.420774},
    {'ask': 0.015500, 'basevolume': 3102.618723, 'bid': 0.015455, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015482, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2159.0, 'opensellorders': 5753.0, 'prevday': 0.017300, 'timestamp': '2017-09-04T16:58:12.513', 'volume': 191555.923339},
    {'ask': 0.015475, 'basevolume': 3105.769030, 'bid': 0.015465, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015475, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2068.0, 'opensellorders': 5757.0, 'prevday': 0.017322, 'timestamp': '2017-09-04T16:59:11.21', 'volume': 191761.558484},
    {'ask': 0.015490, 'basevolume': 3107.413426, 'bid': 0.015450, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015455, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2135.0, 'opensellorders': 5755.0, 'prevday': 0.017325, 'timestamp': '2017-09-04T17:00:09.94', 'volume': 191872.642533},
    {'ask': 0.015500, 'basevolume': 3110.595753, 'bid': 0.015465, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015500, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2217.0, 'opensellorders': 5752.0, 'prevday': 0.017325, 'timestamp': '2017-09-04T17:01:11.683', 'volume': 192086.152654},
    {'ask': 0.015500, 'basevolume': 3112.259338, 'bid': 0.015480, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015500, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2150.0, 'opensellorders': 5754.0, 'prevday': 0.017355, 'timestamp': '2017-09-04T17:02:11.677', 'volume': 192194.489002},
    {'ask': 0.015569, 'basevolume': 3113.453873, 'bid': 0.015505, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015569, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2150.0, 'opensellorders': 5747.0, 'prevday': 0.017326, 'timestamp': '2017-09-04T17:03:10.263', 'volume': 192272.724325},
    {'ask': 0.015569, 'basevolume': 3120.637429, 'bid': 0.015523, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015538, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2154.0, 'opensellorders': 5755.0, 'prevday': 0.017326, 'timestamp': '2017-09-04T17:04:07.96', 'volume': 192736.184784},
    {'ask': 0.015499, 'basevolume': 3126.304975, 'bid': 0.015465, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015499, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2151.0, 'opensellorders': 5752.0, 'prevday': 0.017326, 'timestamp': '2017-09-04T17:05:08.61', 'volume': 193102.305127},
    {'ask': 0.015563, 'basevolume': 3127.906860, 'bid': 0.015410, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015400, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2133.0, 'opensellorders': 5754.0, 'prevday': 0.017326, 'timestamp': '2017-09-04T17:06:08.353', 'volume': 193210.851127},
    {'ask': 0.015556, 'basevolume': 3127.875041, 'bid': 0.015446, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015446, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2175.0, 'opensellorders': 5758.0, 'prevday': 0.017272, 'timestamp': '2017-09-04T17:07:07.8', 'volume': 193214.073586},
    {'ask': 0.015520, 'basevolume': 3129.424044, 'bid': 0.015466, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015520, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2211.0, 'opensellorders': 5757.0, 'prevday': 0.017300, 'timestamp': '2017-09-04T17:08:07.48', 'volume': 193315.304917},
    {'ask': 0.015549, 'basevolume': 3133.105273, 'bid': 0.015500, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015500, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2212.0, 'opensellorders': 5760.0, 'prevday': 0.017226, 'timestamp': '2017-09-04T17:09:02.833', 'volume': 193563.764528},
    {'ask': 0.015530, 'basevolume': 3132.669977, 'bid': 0.015470, 'created': '2014-02-13T00:00:00', 'high': 0.0175, 'last': 0.015470, 'low': 0.015106, 'marketname': 'BTC-LTC', 'openbuyorders': 2220.0, 'opensellorders': 5764.0, 'prevday': 0.017229, 'timestamp': '2017-09-04T17:10:05.733', 'volume': 193554.909540}
])































