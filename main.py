from config import config
from visualizer import Visualizer
from binance_api import BinanceAPI
test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"), recv_windows=config.get("recv_windows"))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    essai = test.get_klines("XRPBTC", interval='1m', delta=7200000)
    visu = Visualizer(essai)
    visu.visu_data()
    """essai = test.get_history("BTCUSDT", 10000)
    for i in essai:
        print(i['time'])
        time = str(i['time'])[:10]
        print(time)
        d = datetime.fromtimestamp(int(time))
        print(d.strftime("%Y/%m/%d, %H:%M:%S"))"""
