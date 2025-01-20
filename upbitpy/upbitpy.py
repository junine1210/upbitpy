# -*- coding: utf-8 -*-
import json
import time
import requests
import jwt
import logging
from urllib.parse import urlencode

import uuid

# https://docs.upbit.com/v1.0/reference
class Upbitpy():
    def __init__(self, access_key=None, secret=None):
        self.access_key = access_key
        self.secret = secret
        self.markets = self._load_markets()

    def _get(self, url, headers=None, data=None, params=None, result_code=200):
        resp = requests.get(url, headers=headers, data=data, params=params)
        if resp.status_code != result_code:
            logging.error('get(%s) failed(%d)' % (url, resp.status_code))
            if resp.text is not None:
                logging.error('resp: %s' % resp.text)
                raise Exception('request.get() failed(%s)' % resp.text)
            raise Exception('request.get() failed(status_code:%d)' % result_code)
        return json.loads(resp.text)

    def _post(self, url, headers, data, result_code=200):
        resp = requests.post(url, headers=headers, data=data)
        if resp.status_code != result_code and resp.status_code != 201:
            logging.error('post(%s) failed(%d)' % (url, resp.status_code))
            if resp.text is not None:
                raise Exception('request.post() failed(%s)' % resp.text)
            raise Exception('request.post() failed(status_code:%d)' % result_code)
        return json.loads(resp.text)

    def _delete(self, url, headers, data, result_code=200):
        resp = requests.delete(url, headers=headers, data=data)
        if resp.status_code != result_code:
            logging.error('delete(%s) failed(%d)' % (url, resp.status_code))
            if resp.text is not None:
                raise Exception('request.delete() failed(%s)' % resp.text)
            raise Exception('request.delete() failed(status_code:%d)' % result_code)
        return json.loads(resp.text)

    def _load_markets(self):
        try:
            market_all = self.get_market_all()
            if market_all is None:
                return
            markets = []
            for market in market_all:
                markets.append(market['market'])
            return markets
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def _get_token(self, query):
        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4())#int(time.time() * 1000),
        }
        if query is not None:
            payload['query'] = urlencode(query)
        return jwt.encode(payload, self.secret, algorithm='HS256').decode('utf-8')

    def _get_headers(self, query=None):
        headers = {'Authorization': 'Bearer %s' % self._get_token(query)}
        return headers

    ###############################################################
    # EXCHANGE API
    ###############################################################

    # https://docs.upbit.com/v1.0/reference#%EC%9E%90%EC%82%B0-%EC%A0%84%EC%B2%B4-%EC%A1%B0%ED%9A%8C

    def get_accounts(self):
        URL = 'https://api.upbit.com/v1/accounts'
        try:
            return self._get(URL, self._get_headers())
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%A3%BC%EB%AC%B8-%EA%B0%80%EB%8A%A5-%EC%A0%95%EB%B3%B4

    def get_chance(self, market):
        URL = 'https://api.upbit.com/v1/orders/chance'
        try:
            if market not in self.markets:
                logging.error('invalid market: %s' % market)
                raise Exception('invalid market: %s' % market)
            data = {'market': market}
            return self._get(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EA%B0%9C%EB%B3%84-%EC%A3%BC%EB%AC%B8-%EC%A1%B0%ED%9A%8C

    def get_order(self, uuid):
        URL = 'https://api.upbit.com/v1/order'
        try:
            data = {'uuid': uuid}
            return self._get(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%A3%BC%EB%AC%B8-%EB%A6%AC%EC%8A%A4%ED%8A%B8-%EC%A1%B0%ED%9A%8C
    # state: 'wait', 'done', 'cancel'
    # order_by: 'asc', 'desc'

    def get_orders(self, market=None, state=None, page=1, order_by='desc'):
        URL = 'https://api.upbit.com/v1/orders'
        try:
            # if market not in self.markets:
            #     logging.error('invalid market: %s' % market)
            #     raise Exception('invalid market: %s' % market)
            #
            # if state not in ['wait', 'done', 'cancel']:
            #     logging.error('invalid state: %s' % state)
            #     raise Exception('invalid state: %s' % state)
            #
            # if order_by not in ['asc', 'desc']:
            #     logging.error('invalid order_by: %s' % order_by)
            #     raise Exception('invalid order_by: %s' % order_by)

            data = {
                'market': market,
                'state': state,
                'page': page,
                'order_by': order_by
            }
            if market == None:
                del data['market']
            if state == None:
                del data['state']
            if page == None:
                del data['page']
            if order_by == None:
                del data['order_by']
            return self._get(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # ~10         : 0.01
    # ~100        : 0.1
    # ~1,000      : 1
    # ~10,000     : 5
    # ~100,000    : 10
    # ~500,000    : 50
    # ~1,000,000  : 100
    # ~2,000,000  : 500
    # +2,000,000  : 1,000

    # def _is_valid_price(self, price):
    #     if price <= 10:
    #         if (price*100) != int(price*100):
    #             return False
    #     elif price <= 100:
    #         if (price*10) != int(price*10):
    #             return False
    #     elif price <= 1000:
    #         if price != int(price):
    #             return False
    #     elif price <= 10000:
    #         if (price % 5) != 0:
    #             return False
    #     elif price <= 100000:
    #         if (price % 10) != 0:
    #             return False
    #     elif price <= 500000:
    #         if (price % 50) != 0:
    #             return False
    #     elif price <= 1000000:
    #         if (price % 100) != 0:
    #             return False
    #     elif price <= 2000000:
    #         if (price % 500) != 0:
    #             return False
    #     elif (price % 1000) != 0:
    #         return False
    #     return True

    def _is_valid_price(self, price):
        return True



    # https://docs.upbit.com/v1.0/reference#%EC%A3%BC%EB%AC%B8%ED%95%98%EA%B8%B0-1
    # side : 'bid'(buy), 'ask'(sell)

    def order(self, market, side, volume, price):
        URL = 'https://api.upbit.com/v1/orders'
        try:
            if market not in self.markets:
                logging.error('invalid market: %s' % market)
                raise Exception('invalid market: %s' % market)

            if side not in ['bid', 'ask']:
                logging.error('invalid side: %s' % side)
                raise Exception('invalid side: %s' % side)

            if not self._is_valid_price(price):
                logging.error('invalid price: %.2f' % price)
                raise Exception('invalid price: %.2f' % price)

            data = {
                'market': market,
                'side': side,
                'volume': str(volume),
                'price': str(price),
                'ord_type': 'limit'
            }
            return self._post(URL, self._get_headers(data), data, result_code=201)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%A3%BC%EB%AC%B8-%EC%B7%A8%EC%86%8C

    def cancel_order(self, uuid):
        URL = 'https://api.upbit.com/v1/order'
        try:
            data = {'uuid': uuid}
            return self._delete(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%A0%84%EC%B2%B4-%EC%B6%9C%EA%B8%88-%EC%A1%B0%ED%9A%8C
    # currency: BTC, ...
    # state: submitting, submitted, almost_accepted, rejected, accepted, processing, done, canceled
    # limit: default:100, max:100

    def get_deposits(self, currency):
        URL = 'https://api.upbit.com/v1/deposits'
        try:
            data = {}
            data['currency'] = currency
            # data['state'] = state
            # data['limit'] = limit
            return self._get(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def get_withraws(self, currency, state, limit):
        LIMIT_MAX = 100
        VALID_STATE = ['submitting', 'submitted', 'almost_accepted',
                       'rejected', 'accepted', 'processing', 'done', 'canceled']
        URL = 'https://api.upbit.com/v1/withdraws'
        try:
            data = {}
            if currency is not None:
                data['currency'] = currency
            if state is not None:
                if state not in VALID_STATE:
                    logging.error('invalid state(%s)' % state)
                    raise Exception('invalid state(%s)' % state)
                data['state'] = state
            if limit is not None:
                if limit <= 0 or limit > LIMIT_MAX:
                    logging.error('invalid limit(%d)' % limit)
                    raise Exception('invalid limit(%d)' % limit)
                data['limit'] = limit
            return self._get(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EA%B0%9C%EB%B3%84-%EC%B6%9C%EA%B8%88-%EC%A1%B0%ED%9A%8C

    def get_withraw(self, uuid):
        URL = 'https://api.upbit.com/v1/withdraw'
        try:
            data = {'uuid': uuid}
            return self._get(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%B6%9C%EA%B8%88-%EA%B0%80%EB%8A%A5-%EC%A0%95%EB%B3%B4

    def get_withraws_chance(self, currency):
        URL = 'https://api.upbit.com/v1/withdraws/chance'
        try:
            data = {'currency': currency}
            return self._get(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%BD%94%EC%9D%B8-%EC%B6%9C%EA%B8%88%ED%95%98%EA%B8%B0

    def withdraws_coin(self, currency, amount, address, secondary_address=None):
        URL = 'https://api.upbit.com/v1/withdraws/coin'
        try:
            data = {
                'currency': currency,
                'amount': amount,
                'address': address
            }
            if secondary_address is not None:
                data['secondary_address'] = secondary_address
            return self._post(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%9B%90%ED%99%94-%EC%B6%9C%EA%B8%88%ED%95%98%EA%B8%B0

    def withdraws_krw(self, amount):
        URL = 'https://api.upbit.com/v1/withdraws/krw'
        try:
            data = {'amount': amount,
                   'two_factor_type': 'kakao'}
            return self._post(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    ###############################################################
    # QUOTATION API
    ###############################################################

    # https://docs.upbit.com/v1.0/reference#%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C

    def get_market_all(self):
        URL = 'https://api.upbit.com/v1/market/all'
        try:
            return self._get(URL)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EB%B6%84minute-%EC%BA%94%EB%93%A4-1
    # unit: 1, 3, 5, 10, 15, 30, 60, 240

    def get_minutes_candles(self, unit, market, to=None, count=None):
        URL = 'https://api.upbit.com/v1/candles/minutes/%s' % str(unit)
        try:
            if unit not in [1, 3, 5, 10, 15, 30, 60, 240]:
                logging.error('invalid unit: %s' % str(unit))
                raise Exception('invalid unit: %s' % str(unit))
            if market not in self.markets:
                logging.error('invalid market: %s' % market)
                raise Exception('invalid market: %s' % market)

            params = {'market': market}
            if to is not None:
                params['to'] = to
            if count is not None:
                params['count'] = count
            return self._get(URL, params=params)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%9D%BCday-%EC%BA%94%EB%93%A4-1

    def get_days_candles(self, market, to=None, count=None):
        URL = 'https://api.upbit.com/v1/candles/days'
        try:
            if market not in self.markets:
                logging.error('invalid market: %s' % market)
                raise Exception('invalid market: %s' % market)

            params = {'market': market}
            if to is not None:
                params['to'] = to
            if count is not None:
                params['count'] = count
            return self._get(URL, params=params)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%A3%BCweek-%EC%BA%94%EB%93%A4-1

    def get_weeks_candles(self, market, to=None, count=None):
        URL = 'https://api.upbit.com/v1/candles/weeks'
        try:
            if market not in self.markets:
                logging.error('invalid market: %s' % market)
                raise Exception('invalid market: %s' % market)
            params = {'market': market}
            if to is not None:
                params['to'] = to
            if count is not None:
                params['count'] = count
            return self._get(URL, params=params)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%9B%94month-%EC%BA%94%EB%93%A4-1

    def get_months_candles(self, market, to=None, count=None):
        URL = 'https://api.upbit.com/v1/candles/months'
        try:
            if market not in self.markets:
                logging.error('invalid market: %s' % market)
                raise Exception('invalid market: %s' % market)
            params = {'market': market}
            if to is not None:
                params['to'] = to
            if count is not None:
                params['count'] = count
            return self._get(URL, params=params)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%8B%9C%EC%84%B8-%EC%B2%B4%EA%B2%B0-%EC%A1%B0%ED%9A%8C

    def get_trades_ticks(self, market, to=None, count=None, cursor=None):
        URL = 'https://api.upbit.com/v1/trades/ticks'
        try:
            if market not in self.markets:
                logging.error('invalid market: %s' % market)
                raise Exception('invalid market: %s' % market)
            params = {'market': market}
            if to is not None:
                params['to'] = to
            if count is not None:
                params['count'] = count
            if cursor is not None:
                params['cursor'] = cursor
            return self._get(URL, params=params)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%EC%8B%9C%EC%84%B8-ticker-%EC%A1%B0%ED%9A%8C

    def get_ticker(self, markets):
        URL = 'https://api.upbit.com/v1/ticker'
        try:
            if not isinstance(markets, list):
                logging.error('invalid parameter: markets should be list')
                raise Exception('invalid parameter: markets should be list')

            if len(markets) == 0:
                logging.error('invalid parameter: no markets')
                raise Exception('invalid parameter: no markets')

            for market in markets:
                if market not in self.markets:
                    logging.error('invalid market: %s' % market)
                    raise Exception('invalid market: %s' % market)

            markets_data = markets[0]
            for market in markets[1:]:
                markets_data += ',%s' % market
            params = {'markets': markets_data}
            return self._get(URL, params=params)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    # https://docs.upbit.com/v1.0/reference#%ED%98%B8%EA%B0%80-%EC%A0%95%EB%B3%B4-%EC%A1%B0%ED%9A%8C

    def get_orderbook(self, markets):
        URL = 'https://api.upbit.com/v1/orderbook?'
        try:
            if not isinstance(markets, list):
                logging.error('invalid parameter: markets should be list')
                raise Exception('invalid parameter: markets should be list')

            if len(markets) == 0:
                logging.error('invalid parameter: no markets')
                raise Exception('invalid parameter: no markets')

            for market in markets:
                if market not in self.markets:
                    logging.error('invalid market: %s' % market)
                    raise Exception('invalid market: %s' % market)

            markets_data = markets[0]
            for market in markets[1:]:
                markets_data += ',%s' % market
            params = {'markets': markets_data}
            return self._get(URL, params=params)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def get_all_address(self):
        URL = 'https://api.upbit.com/v1/deposits/coin_addresses'
        try:
            addresss_ = self._get(URL, self._get_headers())
            for_make_dic_ = {}
            for address_ in addresss_:
                try:
                    if address_['secondary_address'] == None:
                        for_make_dic_.update({address_['currency']:address_['deposit_address']})
                    else:
                        for_make_dic_.update({address_['currency']:address_['deposit_address']+', '+address_['secondary_address']})
                except:
                    continue
            return for_make_dic_
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def get_address(self, currency):
        URL = 'https://api.upbit.com/v1/deposits/generate_coin_address'
        try:
            data = {'currency': currency}
            result_address_ = self._post(URL, self._get_headers(data), data)
            try:
                if result_address_['secondary_address'] == None:
                    return result_address_['deposit_address']
                else:
                    return str(result_address_['deposit_address'] + ' / ' + result_address_['secondary_address'])
            except:
                return result_address_
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def get_address_new(self, currency, net_type):
        URL = 'https://api.upbit.com/v1/deposits/generate_coin_address'
        try:
            data = {'currency': currency, 'net_type': net_type}
            result_address_ = self._post(URL, self._get_headers(data), data)
            try:
                if result_address_['secondary_address'] == None:
                    return result_address_['deposit_address']
                else:
                    return str(result_address_['deposit_address'] + ' / ' + result_address_['secondary_address'])
            except:
                return result_address_
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def get_withraws_chance_new(self, currency, net_type):
        URL = 'https://api.upbit.com/v1/withdraws/chance'
        try:
            data = {'currency': currency, 'net_type': net_type}
            return self._get(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def withdraws_coin_new(self, currency, net_type, amount, address, secondary_address=None):
        URL = 'https://api.upbit.com/v1/withdraws/coin'
        try:
            data = {
                'currency': currency,
                'amount': amount,
                'address': address,
                'net_type': net_type
            }
            if secondary_address is not None:
                data['secondary_address'] = secondary_address
            return self._post(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def get_vasps(self):
        URL = 'https://api.upbit.com/v1/travel_rule/vasps'
        try:
            return self._get(URL, self._get_headers())
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def travel_rule_uuid(self, deposit_uuid, vasp_uuid):
        URL = 'https://api.upbit.com/v1/travel_rule/deposit/uuid'
        try:
            data = {
                'deposit_uuid': deposit_uuid,
                'vasp_uuid': vasp_uuid
            }
            return self._post(URL, self._get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)
