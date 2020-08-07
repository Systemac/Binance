from config import config
from binance_api import BinanceAPI
test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"), recv_windows=config.get("recv_windows"))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(test.get_prices())
    """for _ in range(10):
        result = test.get_products()
        longueur = len(result['symbols'])
        for i in range(longueur):
            print(result['symbols'][i])"""
    """essai = test.get_klines("BTCUSDT", interval="3m", delta=10800, offset=_*3600)
        test.visu_data(essai)"""
    """essai = test.get_history("BTCUSDT", 10000)
    for i in essai:
        print(i['time'])
        time = str(i['time'])[:10]
        print(time)
        d = datetime.fromtimestamp(int(time))
        print(d.strftime("%Y/%m/%d, %H:%M:%S"))"""
