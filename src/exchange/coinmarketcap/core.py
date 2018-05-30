#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests
import tempfile
import requests_cache

class Market(object):

	_session = None
	__DEFAULT_BASE_URL = 'https://api.coinmarketcap.com/v2/'
	__DEFAULT_TIMEOUT = 30
	__TEMPDIR_CACHE = True

	def __init__(self, base_url=__DEFAULT_BASE_URL, request_timeout=__DEFAULT_TIMEOUT, tempdir_cache=__TEMPDIR_CACHE):
		self.base_url = base_url
		self.request_timeout = request_timeout
		self.cache_filename = 'coinmarketcap_cache'
		self.cache_name = os.path.join(tempfile.gettempdir(),
									   self.cache_filename) if tempdir_cache else self.cache_filename

	@property
	def session(self):
		if not self._session:
			self._session = requests_cache.core.CachedSession(cache_name=self.cache_name, backend='sqlite',
															  expire_after=120)
			self._session.headers.update({'Content-Type': 'application/json'})
			self._session.headers.update({'User-agent': 'coinmarketcap - python wrapper around \
	                            coinmarketcap.com (github.com/barnumbirr/coinmarketcap)'})
		return self._session

	def __request(self, endpoint, params):
		response_object = requests.get(self.base_url + endpoint, params = params, timeout = self.request_timeout)

		try:
			response = json.loads(response_object.text)

			# if isinstance(response, list) and response_object.status_code == 200:
			# 	response = [dict(item, **{u'cached':response_object.from_cache}) for item in response]
			# if isinstance(response, dict) and response_object.status_code == 200:
			# 	response[u'cached'] = response_object.from_cache

		except Exception as e:
			return e

		return response

	def listings(self):
		"""
        This endpoint displays all active cryptocurrency listings in one call. Use the
        "id" field on the Ticker endpoint to query more information on a specific
        cryptocurrency.
        """

		response = self.__request('listings/', params=None)
		return response['data']

	def ticker(self, currency="", **kwargs):
		"""
        This endpoint displays cryptocurrency ticker data in order of rank. The maximum
        number of results per call is 100. Pagination is possible by using the
        start and limit parameters.

        GET /ticker/

        Optional parameters:
        (int) start - return results from rank [start] and above (default is 1)
        (int) limit - return a maximum of [limit] results (default is 100; max is 100)
        (string) convert - return pricing info in terms of another currency.
        Valid fiat currency values are: "AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK",
        "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN",
        "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY",
        "TWD", "ZAR"
        Valid cryptocurrency values are: "BTC", "ETH" "XRP", "LTC", and "BCH"

        GET /ticker/{id}

        Optional parameters:
        (string) convert - return pricing info in terms of another currency.
        Valid fiat currency values are: "AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK",
        "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN",
        "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY",
        "TWD", "ZAR"
        Valid cryptocurrency values are: "BTC", "ETH" "XRP", "LTC", and "BCH"
        """

		params = {}
		params.update(kwargs)

		# see https://github.com/mrsmn/coinmarketcap/pull/28
		if currency:
			currency = currency + '/'

		response = ''

		try:
			response = self.__request('ticker/' + currency, params)
			response = [self.normalize_tick(tick) for idx, tick in response['data'].items()]
		except Exception as e:
			print(e)

		return response

	def normalize_tick(self, tick):
		return {
			'id': tick['id'],
			'name': tick['name'],
			'symbol': tick['symbol'],
			'rank': tick['rank'],
			# 'price_btc': self.float_or_none(tick['quotes']['BTC']['price']),
			'price_usd': self.float_or_none(tick['quotes']['USD']['price']),
			'daily_volume_usd': self.float_or_none(tick['quotes']['USD']['volume_24h']),
			'market_cap_usd': self.float_or_none(tick['quotes']['USD']['market_cap']),
			'available_supply': self.float_or_none(tick['circulating_supply']),
			'total_supply': self.float_or_none(tick['total_supply']),
			'percent_change_1h': self.float_or_none(tick['quotes']['USD']['percent_change_1h']),
			'percent_change_24h': self.float_or_none(tick['quotes']['USD']['percent_change_24h']),
			'percent_change_7d': self.float_or_none(tick['quotes']['USD']['percent_change_7d']),
			'last_updated': tick['last_updated']
		}

	@staticmethod
	def float_or_none(item):
		if item is None:
			return item
		else:
			return float(item)

	def stats(self, **kwargs):
		"""
        This endpoint displays the global data found at the top of coinmarketcap.com.

        Optional parameters:
        (string) convert - return pricing info in terms of another currency.
        Valid fiat currency values are: "AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK",
        "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN",
        "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY",
        "TWD", "ZAR"
        Valid cryptocurrency values are: "BTC", "ETH" "XRP", "LTC", and "BCH"
        """

		params = {}
		params.update(kwargs)
		response = self.__request('global/', params)
		return response
