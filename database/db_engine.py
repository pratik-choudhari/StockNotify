from API.tickerprice import StockTicker
from API.alert import send_alert
from config.configkeys import config_keys
import schedule
import time
import os
import sys

import threading
from utils import initlogger
from pymongo import MongoClient


def global_insert(sym, price, chatid):
    try:
        if glob.find_one({'symbol': sym}):
            if glob.find_one({'symbol': sym, f"triggers.{str(price)}": {"$in": [str(chatid)]}}):
                logger.info("Duplicate entry in global")
                return True
            glob.update_one({"symbol": str(sym)}, {"$push": {f"triggers.{str(price)}": str(chatid)}})
        else:
            glob.insert_one({"symbol": str(sym), "triggers": {f"{str(price)}": [str(chatid)]}})
    except Exception as e:
        logger.critical(f"{e} in creating new global trigger")
        return False
    else:
        logger.info(f"insert global -> {chatid} {sym} {price}")
        return True


def new_trigger(chatid: int, symbol: str, price: str):
    """
    Inserts new trigger via telegram into json
    :param chatid: user chatid
    :param symbol: stock symbol
    :param price: price
    :return: True if successful
    """
    try:
        if not global_insert(symbol, price, chatid):
            raise Exception
        if trig.find_one({"client": str(chatid)}):
            if trig.find_one({'client': str(chatid), f"orders.{symbol}": {"$in": [str(price)]}}):
                logger.info("Duplicate entry in user")
                return True
            trig.update_one({"client": str(chatid)}, {"$push": {f"orders.{symbol}": str(price)}})
        else:
            trig.insert_one({"client": str(chatid), "orders": {f"{symbol}": [str(price)]}})
    except Exception as e:
        logger.critical(f"{e} in creating new trigger")
        return False
    else:
        logger.info(f"insert-> {chatid} {symbol} {price}")
        return True


def global_delete(sym, price, chatid):
    try:
        glob.update_one({"symbol": str(sym)}, {"$pull": {f"triggers.{str(price)}": str(chatid)}})
        # check if after pull, array is of size 0 i.e empty
        res = glob.aggregate([{"$match": {"symbol": str(sym)}},
                              {"$project": {"_id": "$symbol","count": {"$size": f"$triggers.{str(price)}"}}}])
        # unset symbol if found empty
        if list(res)[0]['count'] == 0:
            glob.update_one({"symbol": str(sym)}, {"$unset": {f"triggers.{str(price)}": 1}})
            logger.info(f"unset {chatid} {sym}")
            # check if orders exist for the client
            res = glob.find_one({"symbol": str(sym)})
            if not res['triggers']:
                glob.find_one_and_delete({"symbol": str(sym)})
    except KeyError as e:
        logger.critical("Error deleting trigger from db")
        return False
    else:
        logger.info(f"delete global-> {chatid} {sym} {price}")
        return True


def delete_trigger(chatid: int, sym: str, price: str):
    try:
        if not global_delete(sym, price, chatid):
            raise Exception
        trig.update_one({"client": str(chatid)}, {"$pull": {f"orders.{sym}": str(price)}})
        # check if after pull, array is of size 0 i.e empty
        res = trig.aggregate([{"$match": {"client": str(chatid)}}, {"$project": {"_id": "$client",
                                                                                 "count": {
                                                                                     "$size": f"$orders.{sym}"}}}])
        # unset symbol if found empty
        if list(res)[0]['count'] == 0:
            trig.update_one({"client": str(chatid)}, {"$unset": {f"orders.{sym}": 1}})
            logger.info(f"unset {chatid} {sym}")
            # check if orders exist for the client
            res = trig.find_one({"client": str(chatid)})
            if not res['orders']:
                trig.find_one_and_delete({"client": str(chatid)})
    except KeyError as e:
        logger.critical("Error deleting trigger from db")
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
    except KeyError as e:
        logger.critical("Error listing trigger from db")
        return False


def loop_wrapper():
    def screener():
        # check if query data exists before hitting API
        if glob.count():
            syms = glob.distinct('symbol')
            # get price of every distinct stock symbol in db
            for sym in syms:
                ticker.set_sym(sym)
                res = ticker.get_ticker()
                # on successful price fetch
                if res:
                    res = int(res)
                    data = glob.find_one({'symbol': sym})['triggers']
                    # for every price of stock in triggers
                    for price in data.keys():
                        if res >= int(price):
                            # send alert to every subscribed recipient
                            for recipient in data[price]:
                                send_alert(int(recipient), sym, int(price), int(res))
                                delete_trigger(int(recipient), sym, price)
                else:
                    logger.info(f"Error fetching price for {sym}")

    schedule.every(1).minutes.do(screener)
    while True:
        schedule.run_pending()
        time.sleep(1)


if eval(config_keys.get('KEY_FOUND')):
    client = MongoClient('localhost', 27017)

    db = client.stockticker
    trig = db.triggers
    glob = db.globalsymbols

    logger = initlogger.getloggerobj(os.path.basename(__file__))

    global_symbol = {}
    ticker = StockTicker()
    print("polling starts")
    threading.Thread(target=loop_wrapper).start()
else:
    print("polling failed")
    sys.exit(1)
