import json
import threading
import time

import websocket

from binance_api import BinanceAPI
from config import config

test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"), recv_windows=config.get("recv_windows"))
cle = test.get_listenkey()['listenKey']
print(cle)


# def on_message(ws, message):
#     # print("### Message ###")
#     test = json.loads(message)
#     print(test['p'])
#     print(type(test['p']))
#
#
# def on_error(ws, error):
#     print(error)
#
#
# def on_close(ws):
#     print("### closed ###")
#
#
# def on_open(ws):
#     def run(*args):
#         # send the message, then wait
#         # so thread doesn't exit and socket
#         # isn't closed
#         header = {
#             "method": "SUBSCRIBE",
#             "params": [
#                 "btcusdt@aggTrade",
#                 "btcusdt@depth"
#             ],
#             "id": 1}
#
#         ws.send()
#         ws.close()
#         print("Thread terminating...")
#
#     Thread(target=run).start()
#
#
# if __name__ == "__main__":
#     websocket.enableTrace(True)
#     if len(sys.argv) < 2:
#         host = f"wss://stream.binance.com:9443/ws/linkbtc@trade"
#     else:
#         host = sys.argv[1]
#     ws = websocket.WebSocketApp(host,
#                                 on_message=on_message,
#                                 on_error=on_error,
#                                 on_close=on_close)
#     ws.on_open = on_open
#     ws.run_forever()

class WSClient(threading.Thread):
    wsc = None
    stop = False

    def __init__(self, symbol):

        self.symbol = symbol
        threading.Thread.__init__(self)

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
        websocket.enableTrace(True)
        self.wsc = websocket.WebSocketApp(wsc_url,
                                          on_message=self.on_message,
                                          on_error=self.on_error)
        self.wsc.on_open = self.on_open

        while not self.stop:
            self.wsc.run_forever(ping_interval=10)

            if self.stop:
                break

            time.sleep(5)

    def on_error(self, error):
        print("### error ###")
        print(error)

    def on_open(self):
        print("--->[ websocket ]")

    def on_message(self, message):

        test = json.loads(message)
        print(test['p'])
        print(type(test['p']))
        # TODO : generer le prix en local pour l'objet qui contiendra le symbol uniquement.

    def stop_client(self):

        self.stop = True

        if self.wsc is not None:
            self.wsc.close()


a = WSClient(symbol="LINKBTC")
a.start()
time.sleep(15)
a.stop_client()
