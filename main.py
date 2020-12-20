import concurrent.futures
import sys
import time

from binance_api import BinanceAPI
from config.config import config
from algo import follow

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        try:
            test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"),
                              recv_windows=config.get("recv_windows"), percent=config.get('percent'), loop_time=5)
            with concurrent.futures.ThreadPoolExecutor(len(test.assets)) as executor:
                results = executor.map(follow, test.assets)
        except:
            print(f"erreur {sys.exc_info()[0]}")
            time.sleep(5)
