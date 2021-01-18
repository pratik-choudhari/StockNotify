import json
import os
from utils import initlogger
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler
from utils.transactions import new_trigger, query_triggers, delete_trigger
from utils.gettickerprice import StockTicker


# set up logger object
logger = initlogger.getloggerobj(os.path.basename(__file__))
logger.info("Logger init")

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

    gtt_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_cmd)],
        states={
            SYMBOL: [MessageHandler(Filters.regex("^[a-zA-Z0-9: ]+$"), symbol_func)],
            PRICE: [MessageHandler(Filters.regex('^[0-9]+$'), price_func)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    help_handler = CommandHandler('help', help_cmd)
    list_handler = CommandHandler('list', list_triggers)
    update_handler = ConversationHandler(
        entry_points=[CommandHandler('editgtt', list_wrapper)],
        states={
            DELETE: [MessageHandler(Filters.regex("^[0-9]{1}$"), update_triggers)]},
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
        if new_trigger(update.effective_chat.id, sym, thresh):
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Screener set for {sym} at {thresh}, "
                                                                            f"LTP is {currency}{curr}")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="error inserting in db")
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


index_data = {}


def list_triggers(update, context):
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
                text += f"{idx}. {key} at {int(val)}\n"
                index_data[idx] = [key, val]
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return True
    text = "You do not have any GTTs set."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return False


def list_wrapper(update, context):
    ret = list_triggers(update, context)
    if not ret:
        return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Enter gtt number to delete\n")
        return DELETE


def update_triggers(update, context):
    global index_data
    chatid = update.effective_chat.id
    indexes = sorted(list(map(lambda x: int(x), update.message.text.split())))
    logger.debug(f"User indexes: {indexes}")
    op_status = True
    if indexes:
        for idx in indexes:
            if not delete_trigger(chatid, index_data[idx][0], index_data[idx][1]):
                op_status = False
                break
        if not op_status:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Error in deletion in db")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Trigger deleted")
            logger.debug("triggers deleted")
            index_data = {}
        return ConversationHandler.END
    else:
        logger.debug("indexes empty")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Trigger not found")
        index_data = {}
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
