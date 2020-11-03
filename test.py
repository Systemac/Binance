from binance_api import BinanceAPI
from config.config import config

test = BinanceAPI(key=config.get("KEY"), secret=config.get("SECRET"),
                  recv_windows=config.get("recv_windows"), percent=config.get('percent'), loop_time=5)

test.visu_data("YFIBTC")
