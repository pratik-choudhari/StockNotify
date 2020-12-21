from gettickerprice import StockTicker
from sendalert import send_alert

db = {1129060218: {'LON:CEY': ['100', '101'], 'BSE:SBIN' :['325'], 'BSE:HAL': ['345', '637']}}
global_symbol = {'LON:CEY': [1129060218]}
ticker = StockTicker()


def new_trigger(chatid: int, symbol: str, price: str):
    """
    Inserts new trigger via telegram into json
    :param chatid: user id
    :param symbol: stock symbol
    :param price: price
    :return: True if successful
    """
    try:
        if chatid not in db:
            db[chatid] = {symbol: [price]}
        else:
            if symbol not in db[chatid]:
                db[chatid][symbol] = [price]
            else:
                db[chatid][symbol].append(price)
        if symbol not in global_symbol:
            global_symbol[symbol] = [chatid]
        else:
            global_symbol[symbol].append(chatid)
    except Exception as e:
        print(e)
        return False
    else:
        print(db)
        return True


def screener():
    for sym in global_symbol:
        ticker.set_sym(sym)
        res = int(ticker.get_ticker())
        for id in global_symbol[sym]:
            if res >= int(db[id][sym][0]):
                send_alert(id, sym, int(db[id][sym][0]), int(res))


# screener()