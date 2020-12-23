from alpha_vantage.timeseries import TimeSeries
import json

useAPI = False


class StockTicker:
    def __init__(self):
        if useAPI:
            with open("./config/alpha_vantage_api_key.json", "r") as f:
                api_key = json.load(f)
            self.ts = TimeSeries(key=api_key["key"], output_format='pandas')
            self.sym = ""

    def get_ticker(self):
        if not useAPI:
            return 959
        try:
            data, meta_data = self.ts.get_intraday(symbol=self.sym, outputsize="compact", interval="1min")
            return data.iloc[0, 3]
        except ValueError:
            try:
                data, meta_data = self.ts.get_weekly(symbol=self.sym)
                return data.head(1).iloc[0, 3]
            except ValueError:
                return False

    def set_sym(self, symbol):
        self.sym = symbol