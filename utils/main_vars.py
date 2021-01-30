import os
import json
from utils import initlogger
from API.tickerprice import StockTicker


class Variables:
    logger = initlogger.getloggerobj(os.path.basename(__file__))
    logger.info("Logger init")

    ticker = StockTicker()
    SYMBOL, PRICE, DELETE = range(3)
    sym, thresh = "", 0
    nifty_stocks = json.load(open("./assets/nifty_components.json", "r"))['stocks']
