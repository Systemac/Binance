import websocket
from threading import Thread
import time
import sys
import json
from binance_api import BinanceAPI
from config import config

test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"), recv_windows=config.get("recv_windows"))
cle = test.get_listenkey()['listenKey']
print(cle)


def on_message(ws, message):
    # print("### Message ###")
    test = json.loads(message)
    print(test['p'])


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        # send the message, then wait
        # so thread doesn't exit and socket
        # isn't closed
        header = {
            "method": "SUBSCRIBE",
            "params": [
                "btcusdt@aggTrade",
                "btcusdt@depth"
            ],
            "id": 1}

        ws.send()
        ws.close()
        print("Thread terminating...")

    Thread(target=run).start()


if __name__ == "__main__":
    websocket.enableTrace(True)
    if len(sys.argv) < 2:
        host = f"wss://stream.binance.com:9443/ws/xrpbtc@trade"
    else:
        host = sys.argv[1]
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
