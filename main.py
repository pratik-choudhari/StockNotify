import json
import logging

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler
from utils.transactions import new_trigger
from utils.gettickerprice import StockTicker
from buffer import db


track_status = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
stream = logging.StreamHandler()
stream.setFormatter(formatter)
logger.addHandler(stream)

logger.info("App start")
ticker = StockTicker()
SYMBOL, PRICE, DELETE = range(3)
sym, thresh = "", 0
# db = {1129060218: {'LON:CEY': ['100', '101'], 'BSE:SBIN' :['325'], 'BSE:HAL': ['345', '637']}}
# db = {}


def telegrambot():
    with open("config/Telegram_token.json", "r") as f:
        api_key = json.load(f)

    updater = Updater(token=api_key["key"], use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_cmd)],
        states={
            SYMBOL: [MessageHandler(Filters.regex("^[a-zA-Z0-9: ]+$"), symbol_func)],
            PRICE: [MessageHandler(Filters.regex('^[0-9]+$'), price_func)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    help_handler = CommandHandler('help', help_cmd)
    update_handler = ConversationHandler(
        entry_points=[CommandHandler('editgtt', list_triggers)],
        states={
            DELETE: [MessageHandler(Filters.regex("^[0-9]{1}$"), update_triggers)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    unknown_handler = MessageHandler(~Filters.command, unknown)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(update_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(unknown_handler)
    updater.start_polling()
    updater.idle()


def help_cmd(update, context):
    msg = "*Symbols:*\n" \
          " - For indian stocks prefix 'i' or 'I'\n" \
          " - For US stocks directly enter stock symbol.\n" \
          "*Exchange and Currency:*\n" \
          " - Indian stock prices are fetched from BSE and are in INR.\n" \
          " - US stock prices are fetched from NYSE and are in USD.\n" \
          "*Commands:*\n" \
          " - /start to start the conversation\n" \
          " - /cancel to end the conversation\n" \
          " - /editgtt to list and edit triggers\n" \
          "*All LTP displayed are close prices.*"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='markdown')


def start_cmd(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to stock ticker bot📈, "
                                                                    "Use /help to know more, "
                                                                    "please enter stock symbol")
    return SYMBOL


def symbol_func(update, context):
    global sym
    sym = update.message.text.upper()
    if sym[0] == "I":
        sym = "".join(["BSE:", sym[1:]])
    else:
        sym = "".join(["^GSPC:", sym[1:]])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Enter price")
    return PRICE


def price_func(update, context):
    global thresh
    thresh = update.message.text
    logger.info(f"Getting {sym} LTP")
    curr = get_curr_price(sym)
    if sym[:3] == "BSE":
        currency = "₹"
    else:
        currency = "$"
    if curr:
        new_trigger(update.effective_chat.id, sym, thresh)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Screener set for {sym} at {thresh}, "
                                                                        f"LTP is {currency}{curr}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Cannot get LTP")
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(
        'Ending conversation👋'
    )
    return ConversationHandler.END


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def list_triggers(update, context):
    chatid = update.effective_chat.id
    user_data = db.get(chatid)
    logger.info(f"Listing trigger for {chatid}")
    idx = 0
    if user_data:
        keys = list(user_data.keys())
        if keys:
            text = "You have following GTTs set:\n"
            for key in keys:
                for val in db[chatid][key]:
                    idx += 1
                    text += f"{idx}. {key} at {int(val)}\n"
            text += "Enter gtt number to delete\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            return DELETE
    text = "You do not have any GTTs set."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return ConversationHandler.END


def purge_empty(chatid):
    if not db[chatid]:
        del db[chatid]
    keys = list(db[chatid].keys()).copy()
    for key in keys:
        if not db[chatid][key]:
            del db[chatid][key]
    logger.debug(f"{db} after purging {chatid}")


def update_triggers(update, context):
    curr = 0
    chatid = update.effective_chat.id
    indexes = sorted(list(map(lambda x: int(x)-1, update.message.text.split())))
    logger.debug(f"User indexes: {indexes}")
    user_data = db[chatid]
    for key in user_data:
        if indexes:
            if (len(db[chatid][key]) + curr) >= indexes[0]:
                for i in range(len(db[chatid][key])):
                    print(0)
                    if indexes:
                        if indexes[0]-curr == 1:
                            print(i)
                            print('aat')
                            indexes.pop(0)
                            db[chatid][key].pop(i)
                        curr += 1
                    else:
                        purge_empty(chatid)
                        logger.debug("indexes empty")
                        context.bot.send_message(chat_id=update.effective_chat.id, text="Trigger deleted")
                        return ConversationHandler.END
            else:
                curr += len(db[chatid][key]) - 1
    purge_empty(chatid)
    logger.debug("end of stocks")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Trigger not found")
    return ConversationHandler.END


def get_curr_price(s):
    ticker.set_sym(s)
    res = ticker.get_ticker()
    logger.info(f"LTP for {s}: {res}")
    if res:
        return res
    else:
        return False


if __name__ == "__main__":
    telegrambot()
