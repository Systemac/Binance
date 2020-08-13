import json
import threading
import time

import websocket


class WSClient(threading.Thread):
    wsc = None
    stop = False

    def __init__(self, symbol):

        self.symbol = symbol
        threading.Thread.__init__(self)
        self.first_price = 0
        self.price = 0

    def __shortcuts__(self, key):

        if key == "send":
            return self.send
        elif key == "stop":
            return self.stop_client()

        return

    def send(self, message, data=""):

        if self.wsc is None:
            raise ValueError("The websocket client is not started.")

        self.wsc.send(json.dumps({'MessageType': message, "Data": data}))

    def run(self):

        wsc_url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@trade"
        # websocket.enableTrace(True)
        self.wsc = websocket.WebSocketApp(wsc_url,
                                          on_message=self.on_message,
                                          on_error=self.on_error)
        self.wsc.on_open = self.on_open

        while not self.stop:
            self.wsc.run_forever(ping_interval=10)

            time.sleep(5)

    def on_error(self, error):
        print("### error ###")
        print(error)

    def on_open(self):
        print("--->[ websocket ]")

    def on_message(self, message):

        test = json.loads(message)
        if self.first_price == 0:
            self.first_price = float(test['p'])
        self.price = float(test['p'])
        variation = self.price / self.first_price
        # print(
        #     f"{self.symbol} : prix d'achat : {self.first_price}, prix actuel : {self.price}, variation : {round(variation, 4)}")
        if (self.price > self.first_price * 1.003) or (self.price < self.first_price * 0.997):
            print(
                f"{self.symbol}: entrée: {self.first_price}, sortie: {self.price} {'-' if self.first_price > self.price else '+'}")
            print('##### OKI #####')
            self.stop_client()
        # TODO : generer le prix en local pour l'objet qui contiendra le symbol uniquement.

    def stop_client(self):
        self.stop = True
        if self.wsc is not None:
            self.wsc.close()


class Base_de_script:

    def __init__(self, symbol, order=False):
        self.symbol = symbol
        self.order = order

    def suivi(self):
        pass
