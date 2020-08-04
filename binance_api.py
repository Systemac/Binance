import time
import hashlib
import requests
import hmac
from datetime import datetime
import config

try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode


class BinanceAPI:
    BASE_URL = "https://www.binance.com/api/v1"
    BASE_URL_V3 = "https://api.binance.com/api/v3"
    PUBLIC_URL = "https://www.binance.com/exchange/public/product"

    def __init__(self, key, secret, recv_windows):
        self.key = key
        self.secret = secret
        self.recv_windows = recv_windows

    def ping(self):
        path = "%s/ping" % self.BASE_URL_V3
        return requests.get(path, timeout=30, verify=True).json()

    def get_history(self, market, limit=50):
        path = "%s/historicalTrades" % self.BASE_URL
        params = {"symbol": market, "limit": limit}
        return self._get_no_sign(path, params)

    def get_trades(self, market, limit=50):
        path = "%s/trades" % self.BASE_URL
        params = {"symbol": market, "limit": limit}
        return self._get_no_sign(path, params)

    def get_klines(self, market, interval, delta=3600):
        time = self._timestamp(self.get_server_time()['serverTime'])
        path = "%s/klines" % self.BASE_URL_V3
        params = {"symbol": market, "interval": interval, "startTime": time - delta, "endTime": time}
        return self._get_no_sign(path, params)

    def get_ticker(self, market):
        path = "%s/ticker/24hr" % self.BASE_URL
        params = {"symbol": market}
        return self._get_no_sign(path, params)

    def get_order_books(self, market, limit=50):
        path = "%s/depth" % self.BASE_URL
        params = {"symbol": market, "limit": limit}
        return self._get_no_sign(path, params)

    def get_account(self):
        path = "%s/account" % self.BASE_URL_V3
        return self._get(path, {})

    def get_products(self):
        return requests.get(self.PUBLIC_URL, timeout=30, verify=True).json()

    def get_server_time(self):
        path = "%s/time" % self.BASE_URL_V3
        return requests.get(path, timeout=30, verify=True).json()

    def get_exchange_info(self):
        path = "%s/exchangeInfo" % self.BASE_URL
        return requests.get(path, timeout=30, verify=True).json()

    def get_open_orders(self, market, limit=100):
        path = "%s/openOrders" % self.BASE_URL_V3
        params = {"symbol": market}
        return self._get(path, params)

    def get_my_trades(self, market, limit=50):
        path = "%s/myTrades" % self.BASE_URL_V3
        params = {"symbol": market, "limit": limit}
        return self._get(path, params)

    def buy_limit(self, market, quantity, rate):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "BUY", rate)
        return self._post(path, params)

    def sell_limit(self, market, quantity, rate):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "SELL", rate)
        return self._post(path, params)

    def buy_market(self, market, quantity):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "BUY")
        return self._post(path, params)

    def sell_market(self, market, quantity):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "SELL")
        return self._post(path, params)

    def query_order(self, market, order_id):
        path = "%s/order" % self.BASE_URL_V3
        params = {"symbol": market, "orderId": order_id}
        return self._get(path, params)

    def cancel(self, market, order_id):
        path = "%s/order" % self.BASE_URL_V3
        params = {"symbol": market, "orderId": order_id}
        return self._delete(path, params)

    def _get_no_sign(self, path, params={}):
        query = urlencode(params)
        header = {"X-MBX-APIKEY": self.key}
        url = "%s?%s" % (path, query)
        return requests.get(url, timeout=30, verify=True, headers=header).json()

    def _sign(self, params={}):
        data = params.copy()

        ts = int(1000 * time.time())
        data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data

    def _get(self, path, params={}):
        params.update({"recvWindow": self.recv_windows})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        header = {"X-MBX-APIKEY": self.key}
        return requests.get(url, headers=header, \
                            timeout=30, verify=True).json()

    def _post(self, path, params={}):
        params.update({"recvWindow": self.recv_windows})
        query = urlencode(self._sign(params))
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(url, headers=header, data=query, timeout=30, verify=True).json()

    def _order(self, market, quantity, side, rate=None):
        params = {}

        if rate is not None:
            params["type"] = "LIMIT"
            params["price"] = self._format(rate)
            params["timeInForce"] = "GTC"
        else:
            params["type"] = "MARKET"

        params["symbol"] = market
        params["side"] = side
        params["quantity"] = '%.8f' % quantity

        return params

    def _delete(self, path, params={}):
        params.update({"recvWindow": self.recv_windows})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        header = {"X-MBX-APIKEY": self.key}
        return requests.delete(url, headers=header, timeout=30, verify=True).json()

    def _format(self, price):
        return "{:.8f}".format(price)

    def _timestamp(self, server_time):
        time = str(server_time)
        # time = time[:10]
        time = int(time)
        return time

    def _convert_date(self, timestamp):
        date_time = datetime.fromtimestamp(timestamp)
        print(date_time.strftime("%d/%m/%Y %H:%M:%S"))
        return date_time.strftime("%d/%m/%Y %H:%M:%S")

