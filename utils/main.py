import os
import math
import json
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler

from utils import initlogger
from API.tickerprice import StockTicker
from config.configkeys import config_keys
from database.db_engine import new_trigger, query_triggers, delete_trigger

logger, ticker, SYMBOL, PRICE, DELETE, sym, thresh, nifty_stocks = range(8)
index_data = {}


def set_globals():
    """
    sets global variables required for logging and the bot
    :return: None
    """
    global logger, ticker, SYMBOL, PRICE, DELETE, sym, thresh, nifty_stocks
    # set up logger object
    logger = initlogger.getloggerobj(os.path.basename(__file__))
    logger.info("Logger init")

    ticker = StockTicker()
    SYMBOL, PRICE, DELETE = range(3)
    sym, thresh = "", 0
    nifty_stocks = json.load(open("./assets/nifty_components.json", "r"))['stocks']


def telegrambot():
    """
    Driver telegram bot function.
    Includes creation of conversation and command handling
    :return: None
    """
    if not eval(config_keys.get('KEY_FOUND')):
        return False
    set_globals()
    with open(r"./config/Telegram_token.json", "r") as f:
        api_key = json.load(f)

    updater = Updater(token=api_key["key"], use_context=True)
    dispatcher = updater.dispatcher

    gtt_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_cmd)],
        states={
            SYMBOL: [MessageHandler(Filters.regex("^[a-zA-Z0-9: -]+$"), symbol_func)],
            PRICE: [MessageHandler(Filters.regex('^[0-9]+$'), price_func)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    help_handler = CommandHandler('help', help_cmd)
    list_handler = CommandHandler('list', list_triggers)
    update_handler = ConversationHandler(
        entry_points=[CommandHandler('edit', edit_triggers)],
        states={
            DELETE: [MessageHandler(Filters.regex("^[0-9 ]*$"), update_triggers)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    unknown_handler = MessageHandler(~Filters.command, unknown)
    dispatcher.add_handler(list_handler)
    dispatcher.add_handler(gtt_handler)
    dispatcher.add_handler(update_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(unknown_handler)
    updater.start_polling()
    updater.idle()


def help_cmd(update, context):
    """
    send help text to user
    :return: None
    """
    msg = "*Symbols:*\n" \
          " - Only Nifty50 and NiftyNext50 stocks supported." \
          " - Just enter the stock symbol, I will take care of the rest;)\n" \
          "*Exchange and Currency:*\n" \
          " - Indian stock prices are fetched from NSE and are in INR.\n" \
          " - Every price displayed is day close price" \
          "*Commands:*\n" \
          " - /start to start the conversation\n" \
          " - /cancel to end the conversation\n" \
          " - /edit to edit triggers\n" \
          " - /list to list triggers\n" \
          "*Duplicate triggers will be ignore, even if acknowledgement is sent*"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='markdown')


def start_cmd(update, context):
    """
    entry into conversation
    :return: next stage
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to stock ticker bot📈, "
                                                                    "Use /help to know more, "
                                                                    "please enter stock symbol")
    return SYMBOL


def symbol_func(update, context):
    """
    input stock name
    :return: next stage
    """
    global sym
    sym = update.message.text.upper()
    if sym not in nifty_stocks:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Symbol is not in Nifty50 or NiftyNext50")
        return ConversationHandler.END
    context.bot.send_message(chat_id=update.effective_chat.id, text="Enter price")
    return PRICE


def price_func(update, context):
    """
    input trigger price
    :return: next stage
    """
    global thresh
    thresh = float(update.message.text)
    logger.info(f"Getting {sym} LTP")
    curr = get_curr_price(sym)
    if math.isnan(curr):
        context.bot.send_message(chat_id=update.effective_chat.id, text="API returned NaN")
    else:
        if curr > thresh:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"LTP:{curr}. Can't set trigger, only "
                                                                            f"bullish orders")
        elif new_trigger(update.effective_chat.id, sym, thresh):
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Screener set for {sym} at {thresh}, "
                                                                            f"LTP is {curr}")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="error inserting in db")
    return ConversationHandler.END


def cancel(update, context):
    """
    end conversation
    """
    update.message.reply_text(
        'Ending conversation👋'
    )
    return ConversationHandler.END


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def list_triggers(update, context):
    """
    retreive and sent all valid triggers in db for a particular user
    :return: True if successful
    """
    global index_data
    index_data = {}
    chatid = update.effective_chat.id
    user_data = query_triggers(chatid)
    logger.info(f"Listing trigger for {chatid}")
    idx = 0
    if user_data:
        keys = list(user_data.keys())
        text = "You have following GTTs set:\n"
        for key in keys:
            for val in user_data[key]:
                idx += 1
                text += f"{idx}. {key} at {float(val)}\n"
                index_data[idx] = [key, val]
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return True
    text = "You do not have any GTTs set."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return False


def edit_triggers(update, context):
    """
    retreive trigger number to delete
    :return: end conversation or next stage object
    """
    ret = list_triggers(update, context)
    if not ret:
        return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Enter gtt number to delete\n")
        return DELETE


def update_triggers(update, context):
    """
    delete triggers based on user input
    :return: conversation end
    """
    global index_data
    chatid = update.effective_chat.id
    indexes = sorted(list(map(lambda x: int(x), update.message.text.split())))
    logger.info(f"User indexes: {indexes}")
    op_status = True
    idx_error = []
    if indexes:
        for idx in indexes:
            if index_data.get(idx):
                if not delete_trigger(chatid, index_data[idx][0], index_data[idx][1]):
                    op_status = False
                    break
            else:
                idx_error.append(str(idx))
        if idx_error and op_status:
            err = " ".join(idx_error)
            logger.info(f"incorrect indexes {err}")
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Incorrect indexes: {err}"
                                                                            f", other triggers(if any) deleted")
        if not op_status:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Error in deletion in db")
        if not idx_error and op_status:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Trigger(s) deleted")
            logger.debug("triggers deleted")
            index_data = {}
        return ConversationHandler.END
    else:
        logger.info("user entered delete_indexes are empty")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Trigger not found")
        index_data = {}
        return ConversationHandler.END


def get_curr_price(s):
    """
    fetch current stock price
    :param s: symbol
    :return: price
    """
    ticker.set_sym(s)
    res = ticker.get_ticker()
    logger.info(f"LTP for {s}: {res}")

    if res:
        return float(res)
    else:
        return False


if __name__ == "__main__":
    pass
