import time
import hashlib
import requests
import hmac
from datetime import datetime
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
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

    def get_klines(self, market, interval="1m", delta=3600, offset=0):
        delta = delta*1000
        offset = offset*1000
        time = self.get_server_time()['serverTime']
        path = "%s/klines" % self.BASE_URL_V3
        params = {"symbol": market, "interval": interval, "startTime": time-delta-offset, "endTime": time-offset}
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

    def visu_data(self, data):
        reformatted_data = {
            'Date': [],
            'Open': [],
            'High': [],
            'Low': [],
            'Close': [],
            'Volume': [],
        }
        for i in data:
            reformatted_data['Date'].append(datetime.fromtimestamp(self._convert_date(i[0])))
            reformatted_data['Open'].append(float(i[1]))
            reformatted_data['High'].append(float(i[2]))
            reformatted_data['Low'].append(float(i[3]))
            reformatted_data['Close'].append(float(i[4]))
            reformatted_data['Volume'].append(float(i[5]))
        df = pd.DataFrame.from_dict(reformatted_data)
        df.set_index('Date', inplace=True)
        df = self.macd_strat(df)
        df = self.get_rsi_timeseries(df)
        df = self.achat(df)
        print(df)
        fig, ax = plt.subplots(3, sharex=True)
        ax[0].plot(df['Close'], label='test')
        ax[0].plot(df['Achat'], marker=6, color='g')
        ax[0].plot(df['Close'].ewm(span=200).mean(), label='MME 50')
        ax[0].grid(linestyle=':', linewidth='1')
        ax[0].legend(loc='best')
        ax[1].plot(df['RSI'], label='RSI')
        ax[1].axhline(y=30, color='r', label='RSI 30')
        ax[1].axhline(y=70, color='blue', label='RSI 70')
        ax[1].legend(loc='best')
        ax[2].plot(df['macd'], color='k', label='MACD')
        ax[2].plot(df['Signal'], color='r', label='Signal Line')
        secax = ax[2].twinx()
        secax.plot(df['Achat'], marker="|", color='black')
        ax[2].legend(loc='best')
        plt.show()
        mpf.plot(df, type='candle', mav=(7, 14, 26), volume=True)

    def get_rsi_timeseries(self, prices, n=14):
        df_ = prices['Close']
        # RSI = 100 - (100 / (1 + RS))
        # where RS = (Wilder-smoothed n-period average of gains / Wilder-smoothed n-period average of -losses)
        # Note that losses above should be positive values
        # Wilder-smoothing = ((previous smoothed avg * (n-1)) + current value to average) / n
        # For the very first "previous smoothed avg" (aka the seed value), we start with a straight average.
        # Therefore, our first RSI value will be for the n+2nd period:
        #     0: first delta is nan
        #     1:
        #     ...
        #     n: lookback period for first Wilder smoothing seed value
        #     n+1: first RSI
        # First, calculate the gain or loss from one price to the next. The first value is nan so replace with 0.
        deltas = (df_ - df_.shift(1)).fillna(0)
        # Calculate the straight average seed values.
        # The first delta is always zero, so we will use a slice of the first n deltas starting at 1,
        # and filter only deltas > 0 to get gains and deltas < 0 to get losses
        avg_of_gains = deltas[1:n + 1][deltas > 0].sum() / n
        avg_of_losses = -deltas[1:n + 1][deltas < 0].sum() / n
        # Set up pd.Series container for RSI values
        rsi_series = pd.Series(0.0, deltas.index)
        # Now calculate RSI using the Wilder smoothing method, starting with n+1 delta.
        up = lambda x: x if x > 0 else 0
        down = lambda x: -x if x < 0 else 0
        i = n + 1
        for d in deltas[n + 1:]:
            avg_of_gains = ((avg_of_gains * (n - 1)) + up(d)) / n
            avg_of_losses = ((avg_of_losses * (n - 1)) + down(d)) / n
            if avg_of_losses != 0:
                rs = avg_of_gains / avg_of_losses
                rsi_series[i] = 100 - (100 / (1 + rs))
            else:
                rsi_series[i] = 100
            i += 1
        prices['RSI'] = rsi_series
        return prices

    def macd_strat(self, df, petit=12, grand=26, ecart=9):
        df_ = df['Close']
        exp1 = df_.ewm(span=petit, adjust=False).mean()
        exp2 = df_.ewm(span=grand, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['Signal'] = df['macd'].ewm(span=ecart, adjust=False).mean()
        return df

    def achat(self, df):
        df_ = df['RSI'].values
        df_macd = df['macd'].values
        df_signal = df['Signal'].values
        achat = pd.Series(0.0, df.index)
        for i in range(len(df_)):
            if df_[i] > 30:
                if (
                        df_[i - 1] < 30
                        and df_macd[i - 1] < df_macd[i]
                        and df_signal[i - 1] < df_signal[i]
                ):
                    achat[i] = df['Close'][i] - 0.5
            else:
                achat[i] = 0
        df['Achat'] = achat
        df['Achat'][df['Achat'] == 0] = None
        # print(achat[-1])
        return df

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
        time = str(timestamp)
        time = time[:10]
        time = int(time)
        return time

