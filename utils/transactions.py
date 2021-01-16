from utils.gettickerprice import StockTicker
from utils.sendalert import send_alert
import schedule
import time
import logging
import threading
# from buffer import db, global_symbol
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.stockticker
trig = db.triggers
glob = db.globalsymbols

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
stream = logging.StreamHandler()
stream.setFormatter(formatter)
logger.addHandler(stream)

global_symbol = {}
ticker = StockTicker()


def new_trigger(chatid: int, symbol: str, price: str):
    """
    Inserts new trigger via telegram into json
    :param chatid: user chatid
    :param symbol: stock symbol
    :param price: price
    :return: True if successful
    """
    try:
        if trig.find_one({"client": str(chatid)}):
            trig.update_one({"client": str(chatid)}, {"$push": {f"orders.{symbol}": str(price)}})
        else:
            trig.insert_one({"client": str(chatid), "orders": {f"{symbol}": [str(price)]}})
        # if chatid not in db:
        #     db[chatid] = {symbol: [price]}
        # else:
        #     if symbol not in db[chatid]:
        #         db[chatid][symbol] = [price]
        #     else:
        #         db[chatid][symbol].append(price)
        # if symbol not in global_symbol:
        #     global_symbol[symbol] = [chatid]
        # else:
        #     global_symbol[symbol].append(chatid)
    except Exception as e:
        logger.debug(f"{e} in creating new trigger")
        return False
    else:
        logger.info(f"new trigger for {chatid} for {symbol}")
        return True


def delete_trigger(chatid: int, sym: str, price: str):
    try:
        trig.update_one({"client": str(chatid)}, {"$pull": {f"orders.{sym}": str(price)}})
        res = trig.aggregate([{"$match": {"client": "1129060218"}}, {"$project": {"_id": "$client",
                                                                                  "count": {
                                                                                      "$size": "$orders.BSE:HAL"}}}])
        if list(res)[0]['count'] == 0:
            trig.update_one({"client": str(chatid)}, {"$unset": {f"orders.{sym}": ""}})
            logger.info(f"unset {chatid} {sym}")
        # r.hdel(str(chatid), [])
        # db[int(chatid)][sym].remove(price)
        # global_symbol[sym].remove(int(chatid))
    except KeyError as e:
        logger.debug("Error deleting trigger from db")
        return False
    else:
        logger.info(f"delete-> {chatid} {sym} {price}")
        return True


def query_triggers(chatid: int):
    try:
        res = trig.find_one({"client": str(chatid)})
        if res:
            return res['orders']
        else:
            return False
        # r.hdel(str(chatid), [])
        # db[int(chatid)][sym].remove(price)
        # global_symbol[sym].remove(int(chatid))
    except KeyError as e:
        logger.debug("Error listing trigger from db")
        return False


def loop_wrapper():
    def screener():
        if global_symbol:
            for sym in global_symbol:
                ticker.set_sym(sym)
                res = int(ticker.get_ticker())
                for chatid in global_symbol[sym]:
                    if res >= int(db[chatid][sym][0]):
                        send_alert(int(chatid), sym, int(db[chatid][sym][0]), int(res))
                        delete_trigger(int(chatid), sym, db[chatid][sym][0])

    schedule.every(1).minutes.do(screener)
    while True:
        schedule.run_pending()
        time.sleep(1)


threading.Thread(target=loop_wrapper).start()
