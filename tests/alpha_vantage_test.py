from alpha_vantage.timeseries import TimeSeries
import json


class StockTicker:
    def __init__(self):
        with open("../config/alpha_vantage_api_key.json", "r") as f:
            api_key = json.load(f)
        self.ts = TimeSeries(key=api_key["key"], output_format='pandas')
        self.sym = ""

    def get_ticker(self):
        try:
            data, meta_data = self.ts.get_intraday(symbol=self.sym, outputsize="compact", interval="1min")
            print(data)
            return data
        except ValueError:
            data, meta_data = self.ts.get_weekly(symbol=self.sym)
            print(data)
            return data.head(1).iloc[0, :]

    def set_sym(self, symbol):
        self.sym = symbol


if __name__ == "__main__":
    ticker = StockTicker()
    ticker.set_sym("BSE:532659")
    print(ticker.get_ticker())