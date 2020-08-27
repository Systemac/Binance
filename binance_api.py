import datetime
import hashlib
import hmac
import math
import random
import time

import mplfinance as mpf
import numpy as np
import pandas as pd
import requests

from websocket_api import WSClient

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
        self.portfolio = {}
        self.assets = []
        self.products = self.get_products()
        self.get_portfolio()
        self.get_assets_to_follow()

    def truncate(self, number, digits) -> float:
        if digits < 0:
            digits += 1
        stepper = 10.0 ** digits
        return math.trunc(stepper * number) / stepper

    def follow(self, asset):
        _nowt = datetime.datetime.now()
        while True:
            if datetime.datetime.now() > _nowt + datetime.timedelta(minutes=10):
                break
            # print(f"Début suivi sur {asset}")
            orders = self.get_open_orders(asset)
            for j in self.portfolio:
                if j == asset[:-3] and self.portfolio[j]['free'] != 0:
                    for k in self.products['symbols']:
                        if k['symbol'] == f"{j}BTC" and float(
                                k['filters'][2]['minQty']
                        ) < float(self.portfolio[j]['free']):
                            print(
                                f"Assez de fond sur {j}BTC: {k['filters'][2]['minQty']} {self.portfolio[j]['free']}")
                            # print("OK")
                            # print(f"{asset} : {self.get_my_trades(asset)[0]['price']} {type(self.get_my_trades(asset)[0]['price'])}")
                            t = WSClient(open_price=float(self.get_my_trades(asset)[-1]['price']), symbol=asset)
                            t.start()
                            _now1 = datetime.datetime.now()
                            while True:
                                if datetime.datetime.now() > _now1 + datetime.timedelta(minutes=10):
                                    # self.follow(asset)
                                    t.stop_client()  # TODO : mettre ceci en méthode et changer la sortie pour qu'il y ai une condition sur le fait que le prix corresponde ou non à l'attente.
                                    print(f"Fin de boucle pour {asset}.")
                                    sys.exit(0)
                                    break
                                elif not t.is_alive():
                                    print(f"Sortie de boucle pour {asset}, 2 % atteint !!")
                                    orders = self.get_open_orders(asset)
                                    print(orders)
                                    if len(orders) != 0:
                                        _order = self.get_prices()
                                        for _ in _order:
                                            if _['symbol'] == asset:
                                                price_order = float(_['price'])
                                        order_id = orders[0]['orderId']
                                        self.cancel(asset, order_id)
                                    else:
                                        _order = self.get_prices()
                                        for _ in _order:
                                            if _['symbol'] == asset:
                                                price_order = float(_['price'])
                                        print("Pas d'ordre")
                                    print(self.stop_loss_limit(market=asset,
                                                               quantity=self.calcul_quantity(asset),
                                                               price=self.calcul_precision_price(asset,
                                                                                                 float(
                                                                                                     self.get_prices_asset(
                                                                                                         asset)) * 0.99)))
                            time.sleep(0.1)
                        self.get_portfolio()
                if orders:
                    price_order = float(orders[0]['price'])
                    print(f"Ordre en cours sur {asset} à {price_order}")
                    t = WSClient(open_price=price_order, symbol=asset)
                    t.start()
                    _now = datetime.datetime.now()
                    while True:
                        if datetime.datetime.now() > _now + datetime.timedelta(minutes=10):
                            # self.follow(asset)
                            t.stop_client()
                            print(f"Fin de boucle pour {asset}.")
                            sys.exit(0)
                            break
                        elif not t.is_alive():
                            orders = self.get_open_orders(asset)
                            if orders:
                                order_id = orders[0]['orderId']
                                self.cancel(asset, order_id)
                            print(self.stop_loss_limit(market=asset,
                                                       quantity=self.calcul_quantity(asset),
                                                       price=self.calcul_precision_price(asset,
                                                                                         float(self.get_prices_asset(
                                                                                             asset)) * 0.99)))
                            break
                        time.sleep(0.1)
                    self.get_portfolio()
                elif self.get_opportunity(self.get_klines(asset)):
                    print(f"Opportunité sur {asset} !!!!!")
                    self.buy_market(market=asset, quantity=self.calcul_quantity(asset))
                    p_open = float(self.get_my_trades(asset)[-1]['price'])
                    t = WSClient(open_price=p_open, symbol=asset)
                    t.start()
                    _now = datetime.datetime.now()
                    while True:
                        if datetime.datetime.now() > _now + datetime.timedelta(minutes=10):
                            # self.follow(asset)
                            t.stop_client()
                            sys.exit(0)
                            break
                        elif not t.is_alive():
                            print(self.stop_loss_limit(market=asset,
                                                       quantity=self.calcul_quantity(asset),
                                                       price=self.calcul_precision_price(asset,
                                                                                         float(self.get_prices_asset(
                                                                                             asset)) * 0.99)))
                            self.get_portfolio()
                            break
                        time.sleep(0.1)
                time.sleep(random.randint(10, 30))
        print(f"Fin de boucle sur {asset}")

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

    def get_klines(self, market, interval="1m", delta=200000, offset=0):
        delta = delta * 1000
        offset = offset * 1000
        times = self.get_server_time()['serverTime']
        path = "%s/klines" % self.BASE_URL_V3
        params = {"symbol": market, "interval": interval, "startTime": times - delta - offset,
                  "endTime": times - offset}
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

    def get_portfolio(self):
        data = self.get_account()
        dico = {}
        for _ in data['balances']:
            if float(_['free']) != 0:
                dico[_['asset']] = {
                    'free': float(_['free']),
                    'locked': float(_['locked'])}
        self.portfolio = dico

    def get_assets_to_follow(self):
        i = self.portfolio
        # print(i)
        for j in i:
            if i[j]['locked'] != 0:
                self.assets.append(f"{j}BTC")
            elif i[j]['free'] != 0:
                for k in self.products['symbols']:
                    if k['symbol'] == f"{j}BTC":
                        print(f"{j}BTC: {k['filters'][2]['minQty']} {i[j]['free']}")
                        if float(k['filters'][2]['minQty']) < i[j]['free']:
                            print("OK")
                            self.assets.append(f"{j}BTC")
                        else:
                            print("KO")
        l = self.get_sorted_symbol_by_volume()
        k = 0
        while len(self.assets) < 5:
            if l[k][0] not in self.assets:
                self.assets.append(l[k][0])
            k += 1
        print(self.assets)

    def get_sorted_symbol_by_volume(self):
        essai = self.get_prices()
        essai2 = self.get_prices_change()
        liste = []
        for i in essai:
            if i['symbol'][-3:] == 'BTC':
                for j in essai2:
                    if j['symbol'] == i['symbol']:
                        volume = float(i["price"]) * float(j['volume'])
                        liste.append((i["symbol"], float(i["price"]), volume))
        return sorted(liste, key=lambda price: price[2], reverse=True)

    def get_prices(self):
        path = "%s/ticker/price" % self.BASE_URL_V3
        return self._get_no_sign(path)

    def get_prices_asset(self, asset):
        path = f"{self.BASE_URL_V3}/ticker/price"
        params = {"symbol": asset}
        return self._get_no_sign(path, params).get("price")

    def get_prices_change(self):
        path = "%s/ticker/24hr" % self.BASE_URL_V3
        return self._get_no_sign(path)

    def get_products(self):
        path = "%s/exchangeInfo" % self.BASE_URL_V3
        return requests.get(path, timeout=30, verify=True).json()

    def get_server_time(self):
        path = "%s/time" % self.BASE_URL_V3
        return requests.get(path, timeout=30, verify=True).json()

    def get_listenkey(self):
        path = "%s/userDataStream" % self.BASE_URL_V3
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(path, headers=header).json()

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

    def calcul_quantity(self, asset):
        btc_free = self.portfolio['BTC']['free'] / 3
        print(btc_free)
        # print(type(btc_free))
        essai = self.get_prices()
        # ca doit donc etre un multiple de ca
        for i in self.products['symbols']:
            if i['symbol'] == asset:
                for j in essai:
                    if j['symbol'] == asset:
                        print(
                            f"{i['filters'][2]['minQty']} : {i['filters'][2]['minQty'].find('1')} : {i['filters'][2]['minQty'].find('.')}")
                        rec = i['filters'][2]['minQty'].find('1') - i['filters'][2]['minQty'].find('.')
                        print(rec)
                        amount = btc_free / float(j['price'])
                        quantity = self.truncate(amount, rec)
                        print(
                            f"{i['symbol']}: {i['filters'][2]['minQty']}  {amount} / {quantity}")
        return quantity

    def calcul_quantity_sell(self, asset):
        for _ in self.products['symbols']:
            if _['symbol'] == asset:
                minqty = float(_['filters'][2]['minQty'])
                amount = self.portfolio[f"{asset[:-3]}"]['free']
                rec = _['filters'][2]['minQty'].find('1') - _['filters'][2]['minQty'].find('.')
                quantity = self.truncate(amount, rec)
                # print(f"{minqty}, {amount}, {quantity}")
        return quantity

    def calcul_precision_price(self, asset, price):
        for _ in self.products['symbols']:
            if _['symbol'] == asset:
                precision = int(_['baseAssetPrecision'])
                true_price = self.truncate(price, precision)
                print(f"true price {true_price}")
        return true_price

    def buy_limit(self, market, quantity, rate):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "BUY", rate)
        return self._post(path, params)

    def stop_loss(self, market, quantity, price):
        path = "%s/order" % self.BASE_URL_V3
        params = {
            'symbol': market,
            'side': 'SELL',
            'type': 'STOP_LOSS',
            'stopPrice': price,
            'quantity': quantity
        }
        return self._post(path, params)

    def stop_limit(self, market, quantity, price):
        path = "%s/order" % self.BASE_URL_V3
        params = {
            'symbol': market,
            'side': 'SELL',
            'type': 'LIMIT',
            "timeInForce": "GTC",
            'price': price,
            'quantity': quantity
        }
        return self._post(path, params)

    def stop_loss_limit(self, market, quantity, price):
        path = "%s/order" % self.BASE_URL_V3
        params = {
            'symbol': market,
            'side': 'SELL',
            'type': 'STOP_LOSS_LIMIT',
            "timeInForce": "GTC",
            'price': price,
            'stopPrice': price,
            'quantity': quantity
        }
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

    def _prepa_visu_or_opportunity(self, data):
        reformatted_data = {
            'Date': [],
            'Open': [],
            'High': [],
            'Low': [],
            'Close': [],
            'Volume': [],
        }
        for i in data:
            reformatted_data['Date'].append(datetime.datetime.fromtimestamp(self._convert_date(i[0])))
            reformatted_data['Open'].append(float(i[1]))
            reformatted_data['High'].append(float(i[2]))
            reformatted_data['Low'].append(float(i[3]))
            reformatted_data['Close'].append(float(i[4]))
            reformatted_data['Volume'].append(float(i[5]))
        df = pd.DataFrame.from_dict(reformatted_data)
        df.set_index('Date', inplace=True)
        df = self.macd_strat(df)
        df = self.get_rsi_timeseries(df)
        df = self.bollinger_band(df)
        df = self.achat(df)
        df['lowSignal'] = self._percentB_belowzero(df)
        df['highSignal'] = self._percentB_aboveone(df)
        # print(df)
        return df

    def _get_opportunity(self, data):
        df = self._prepa_visu_or_opportunity(data)
        return not math.isnan(df.iloc[-1, -2])

    def get_opportunity(self, data):
        # print(achat)
        return self._get_opportunity(data)

    def visu_data(self, dfi):
        df = self._prepa_visu_or_opportunity(dfi)
        for _ in df:
            df['RSI30'] = 30
            df['RSI70'] = 70
        df.tail()
        boll = df[['MB', 'HighB', 'LowB']]
        rsi = df[['RSI', 'RSI30', 'RSI70']]
        apt = [mpf.make_addplot(boll),
               mpf.make_addplot(df['lowSignal'], type='scatter', markersize=200, marker='^'),
               mpf.make_addplot(df['highSignal'], type='scatter', markersize=200, marker='v'),
               mpf.make_addplot(df['percentB'], panel=2, color='r'),
               mpf.make_addplot(rsi, panel=2, color='g'),
               mpf.make_addplot(df["macd"], color='black', panel=3),
               mpf.make_addplot(df["Signal"], color='r', panel=3)]
        mpf.plot(df, type='candle', figscale=1.25, volume=True, addplot=apt)

    def _percentB_belowzero(self, df):
        percentB = df['percentB']
        price = df['Close']
        rsi = df['RSI']
        signal = []
        previous = -1.0
        for date, value in percentB.iteritems():
            if value < 0 <= previous and rsi[date] < 30:
                signal.append(price[date])
            else:
                signal.append(np.nan)
            previous = value
        return signal

    def _percentB_aboveone(self, df):
        percentB = df['percentB']
        price = df['Close']
        rsi = df['RSI']
        signal = []
        previous = 2
        for date, value in percentB.iteritems():
            if value > 1 >= previous:
                signal.append(price[date])
            else:
                signal.append(np.nan)
            previous = value
        return signal

    def bollinger_band(self, df, fenetre=20, std=2):
        df['MB'] = df['Close'].rolling(fenetre).mean()
        rolling_std = df['Close'].rolling(fenetre).std()
        df['HighB'] = df['MB'] + (rolling_std * std)
        df['LowB'] = df['MB'] - (rolling_std * std)
        df['percentB'] = (df['Close'] - df['LowB']) / (df['HighB'] - df['LowB'])
        return df

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
        url = "%s" % path
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
