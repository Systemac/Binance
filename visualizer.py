import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from binance_api import BinanceAPI


class Visualizer:

    def __init__(self, data):
        self.data = data

    def visu_data(self):
        reformatted_data = dict()
        reformatted_data['Date'] = []
        reformatted_data['Open'] = []
        reformatted_data['High'] = []
        reformatted_data['Low'] = []
        reformatted_data['Close'] = []
        reformatted_data['Volume'] = []
        for i in self.data:
            reformatted_data['Date'].append(datetime.fromtimestamp(self._convert_date(i[0])))
            reformatted_data['Open'].append(float(i[1]))
            reformatted_data['High'].append(float(i[2]))
            reformatted_data['Low'].append(float(i[3]))
            reformatted_data['Close'].append(float(i[4]))
            reformatted_data['Volume'].append(float(i[5]))
        df = pd.DataFrame.from_dict(reformatted_data)
        df.set_index('Date', inplace=True)
        print(df)
        mpf.plot(df, type='candle', mav=(7, 14, 26), volume=True)


