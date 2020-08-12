from binance_api import BinanceAPI
from config import config

test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"), recv_windows=config.get("recv_windows"))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test.get_portfolio()
    liste = []
    i = test.portfolio
    for j in i:
        if i[j]['locked'] != 0:
            print(i[j]['locked'], j)
            liste.append(f"{j}BTC")
            print(test.get_open_orders(f"{j}BTC"))
    print(liste)
    # essai = test.get_klines("ANKRBTC", interval="5m", delta=200000)
    # test.visu_data(essai)
    # test.get_sorted_symbol_by_volume()
    # for i in test.sorted_btc[:10]:
    #     print(i[2])
