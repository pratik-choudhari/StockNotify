from alpha_vantage.timeseries import TimeSeries
import json
import yfinance as yf
import datetime


class StockTicker:
    def __init__(self):
        with open("../config/alpha_vantage_api_key.json", "r") as f:
            api_key = json.load(f)
        self.ts = TimeSeries(key=api_key["key"], output_format='pandas')
        self.sym = ""

    def get_ticker(self):
        if datetime.datetime.today().weekday() not in [5, 6]:
            try:
                data, _ = self.ts.get_intraday(symbol=self.sym, outputsize="compact", interval="1min")
                return data
            except ValueError:
                return False
        else:
            try:
                data, _ = self.ts.get_weekly(symbol=self.sym)
                return yf.Ticker(self.sym+".NS").history(period='1d').iloc[0, 3]
            except ValueError:
                return False

    def set_sym(self, symbol):
        self.sym = symbol


if __name__ == "__main__":
    ticker = StockTicker()
    ticker.set_sym("BSE:TECHM")
    print(ticker.get_ticker())
