import datetime
import random
import time

from binance_api import BinanceAPI
from config.config import config
from telegram import senders

ba = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"),
                recv_windows=config.get("recv_windows"), percent=config.get('percent'), loop_time=5)


def follow(asset):
    _nowt = datetime.datetime.now()
    while True:
        if datetime.datetime.now() > _nowt + datetime.timedelta(minutes=ba.loop_time):
            break
        # print(f"Début suivi sur {asset}")
        i = ba.portfolio
        # print(i)
        # print(asset[:-3])
        if asset[:-3] in i:
            # print(f"{asset[:-3]} {asset} présent !!!!")
            # print(f"j : {j}, asset : {asset}")
            if ba.portfolio[asset[:-3]]['free'] != 0:
                # print("ok")
                for k in ba.products['symbols']:
                    # print(f"k : {k}")
                    if k['symbol'] == asset:
                        print(
                            f"{asset} min : {float(k['filters'][2]['minQty'])} avail : {ba.portfolio[asset[:-3]]['free']}")
                        if float(k['filters'][2]['minQty']) < float(i[asset[:-3]]['free']):
                            t = ba.get_my_trades(asset)
                            # print(f"my trades : {t} len: {len(t)}")
                            if len(t) > 1:
                                t = ba.get_last_buy(asset)
                                aaa = float(t) * ba.percent
                                ccc = float(t) * 0.90
                                bbb = float(ba.get_prices_asset(asset=asset))
                                print(
                                    f"Valeur d'achat sur {asset}: {ba.get_last_buy(asset)} actuel: {ba.get_prices_asset(asset=asset)}")
                                # print(f"asset : {asset} aaa: {float(aaa)}, bbb: {bbb}")
                                if float(aaa) <= bbb:
                                    print(
                                        f"Opportunité vente sur {asset}, prix achat: {t}, prix vente : {ba.get_prices_asset(asset=asset)} !!!!!")
                                    ba.sell_market(market=asset, quantity=ba.calcul_quantity_sell(asset))
                                    senders(
                                        f"Opportunité vente sur {asset}, prix achat: {t}, prix vente : {ba.get_prices_asset(asset=asset)} !!!!!")
                                    time.sleep(2)
                                    ba.get_portfolio()
                                if float(ccc) >= bbb:
                                    print(
                                        f"Vente de {asset}, prix achat: {t}, prix vente : {ba.get_prices_asset(asset=asset)}, trop forte baisse.")
                                    ba.sell_market(market=asset, quantity=ba.calcul_quantity_sell(asset))
                                    senders(
                                        f"Vente de {asset}, prix achat: {t}, prix vente : {ba.get_prices_asset(asset=asset)}, trop forte baisse.")
                                    time.sleep(2)
                                    ba.get_portfolio()
                            else:
                                if ba.get_opportunity_sell(ba.get_klines(asset)):
                                    ba.sell_market(market=asset, quantity=ba.calcul_quantity_sell(asset))
                                    time.sleep(2)
                                    ba.get_portfolio()
                            time.sleep(random.randint(6, 12))
                        else:
                            # print(f'le else : {asset}')
                            if ba.get_opportunity_buy(ba.get_klines(asset)):
                                opportunity_buy(asset)
                        time.sleep(random.randint(10, 20))
        else:
            print(f"Pas assez de fond sur {asset}, suivi en cours pour achat...")
            if ba.get_opportunity_buy(ba.get_klines(asset)):
                opportunity_buy(asset)
            time.sleep(random.randint(6, 12))
    time.sleep(random.randint(10, 20))
    print(f"Fin de boucle sur {asset}")


def opportunity_buy(asset):
    print(f"Opportunité achat sur {asset} !!!!!")
    ba.buy_market(market=asset, quantity=ba.calcul_quantity(asset))
    senders(f"Opportunité achat sur {asset} !!!!!")
    time.sleep(random.randint(6, 12))
    ba.get_portfolio()
