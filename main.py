from gettickerprice import StockTicker
import json
from transactions import new_trigger
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler
# from telegramutils import telegrambot

track_status = False


ticker = StockTicker()
SYMBOL, PRICE, DELETE = range(3)
sym, thresh = "", 0
# db = {1129060218: {'LON:CEY': ['100', '101'], 'BSE:SBIN' :['325'], 'BSE:HAL': ['345', '637']}}
db = {}


def telegrambot():
    with open("Telegram_token.json", "r") as f:
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
    id = update.effective_chat.id
    user_data = db.get(id)
    if user_data:
        keys = list(user_data.keys())
        if keys:
            text = "You have following GTTs set:\n"
            for key in keys:
                for val in db[id][key]:
                    text += f"{key} at {int(val)}\n"
            text += "Enter gtt number to delete\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            return DELETE
    text = "You do not have any GTTs set."
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return ConversationHandler.END


def update_triggers(update, context):
    curr = 0
    id = update.effective_chat.id
    indexes = sorted(list(map(lambda x: int(x)-1, update.message.text.split())))
    print(indexes)
    for key in db[id]:
        if indexes:
            if (len(db[id][key])+curr) >= indexes[0]:
                for i in range(len(db[id][key])):
                    if indexes:
                        if indexes[0]-curr == 1:
                            print(i)
                            print('aat')
                            indexes.pop(0)
                            db[id][key].pop(i)
                        curr += 1
                    else:
                        print(db)
                        return ConversationHandler.END
            else:
                print(db)
                return ConversationHandler.END
        else:
            curr += len(db[id][key])-1
    print(db)
    return ConversationHandler.END


def get_curr_price(s):
    ticker.set_sym(s)
    res = ticker.get_ticker()
    print(res)
    if res:
        return res
    else:
        return False


if __name__ == "__main__":
    telegrambot()
