from alpha_vantage.timeseries import TimeSeries
import json
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler
# from telegramutils import telegrambot

track_status = False


class StockTicker:
    def __init__(self):
        with open("alpha_vantage_api_key.json", "r") as f:
            api_key = json.load(f)
        self.ts = TimeSeries(key=api_key["key"], output_format='pandas')
        self.sym = ""

    def get_ticker(self):
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


ticker = StockTicker()
SYMBOL, PRICE = range(2)
sym, thresh = "", 0


def telegrambot():
    with open("Telegram_token.json", "r") as f:
        api_key = json.load(f)

    updater = Updater(token=api_key["key"], use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_cmd)],
        states={
            SYMBOL: [MessageHandler(Filters.regex("^[a-zA-Z: ]+$"), symbol_func)],
            PRICE: [MessageHandler(Filters.regex('^[0-9]+$'), price_func)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    help_handler = CommandHandler('help', help_cmd)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(help_handler)
    unknown_handler = MessageHandler(~Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)
    updater.start_polling()
    updater.idle()


def help_cmd(update, context):
    msg = "*Symbols:*\n" \
          " - For indian stocks prefix 'i' or 'I'\n" \
          " - For US stocks directly enter stock symbol.\n" \
          "*Exchange and Currency:*\n" \
          " - Indian stock price are fetched from BSE and are in INR.\n" \
          " - US stock price is fetched from NYSE and are in USD.\n" \
          "*All LTP displayed are close prices.*"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='markdown')


def start_cmd(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to stock ticker bot, "
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
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Screener set for {sym} at {thresh}, "
                                                                        f"LTP is {currency}{curr}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Cannot get LTP")


def cancel(update, context):
    update.message.reply_text(
        'Bye! Ending Conversation.'
    )
    return ConversationHandler.END


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


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
