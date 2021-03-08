import json

import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from config.configkeys import config_keys

useAPI = config_keys['USE_API']
if useAPI:
    print("Using alpha vantage API")
else:
    print("Using yfinance API")


class StockTicker:
    def __init__(self):
        if useAPI:
            with open("./config/alpha_vantage_api_key.json", "r") as f:
                api_key = json.load(f)
            self.ts = TimeSeries(key=api_key["key"], output_format='pandas')
            self.sym = ""

    def get_ticker(self):
        if useAPI:
            try:
                data, meta_data = self.ts.get_intraday(symbol=self.sym, outputsize="compact", interval="1min")
                return data.iloc[0, 3]
            except ValueError:
                return False
        else:
            try:
                return '{0:.2f}'.format(yf.Ticker(self.sym + ".NS").history(period='1d').iloc[0, 3])
            except [ValueError, IndexError]:
                return False

    def set_sym(self, symbol):
        self.sym = symbol
