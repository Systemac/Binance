# This is a sample Python script.
from config import config
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests

BASE_URL = "https://api.binance.com"


def test_connectivity():
    response = requests.get(BASE_URL + "/api/v3/ping")
    print(response)
    print(response.json())


def check_server_time():
    response = requests.get(BASE_URL + "/api/v3/time")
    print(response)
    print(response.json())


def check_exchange_information():
    response = requests.get(BASE_URL + "/api/v3/exchangeInfo")
    # print(response)
    print(response.json())


def order_book(symbol, limit=100):
    params = {
        'symbol': symbol,
        'limit': limit
    }
    response = requests.get(BASE_URL + "/api/v3/depth", params=params)
    # print(response)
    print(response.json())


def historical_book(symbol, limit=500):
    headers = {
        'X-MBX-APIKEY': config.get("KEY")
    }
    params = {
        'symbol': symbol,
        'limit': limit
    }
    response = requests.get(BASE_URL + "/api/v3/historicalTrades", params=params, headers=headers)
    # print(response)
    print(response.json())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    historical_book('ETHBTC')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
