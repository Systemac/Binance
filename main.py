import concurrent.futures
import time

from binance_api import BinanceAPI
from config import config

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"),
    #                   recv_windows=config.get("recv_windows"))
    # print((test.get_prices_asset("ETHBTC")))
    # print((type(test.get_prices_asset("ETHBTC"))))
    # print(test.get_my_trades("LINKBTC")[-1])
    # test.calcul_quantity_sell("LINKBTC")
    # test.follow("LINKBTC")
    # while True:
    # test.calcul_precision_("LINKBTC")
    #     for i in test.assets:
    #         print(i)
    #         if test.get_opportunity(test.get_klines(i)):
    #             print(f"Opportunité !!!!!!!!!!")
    #             break
    #         else:
    #             print("Pas encore...")
    #     time.sleep(3)
    # for _ in test.assets:
    #     _ = WSClient(_)
    #     _.start()
    #     print(_.getName())

    while True:
        try:
            test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"),
                              recv_windows=config.get("recv_windows"))
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(test.assets)) as executor:
                results = executor.map(test.follow, test.assets)
        except:
            time.sleep(30)
    # for i in test.assets:
    #     test.calcul_quantity(i)
    # print(test.get_my_trades("ETHBTC"))
    # print(test.sell_limit("ETHBTC", 0.027, rate=None))
    # liste = []
    # i = test.portfolio
    # for j in i:
    #     if i[j]['locked'] != 0:
    #         print(i[j]['locked'], j)
    #         liste.append(f"{j}BTC")
    #         print(test.get_open_orders(f"{j}BTC"))
    # print(liste)
    # essai = test.get_klines("ANKRBTC", interval="5m", delta=200000)
    # test.visu_data(essai)
    # test.get_sorted_symbol_by_volume()
    # for i in test.sorted_btc[:10]:
    #     print(i[2])
