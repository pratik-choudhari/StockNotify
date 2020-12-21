from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler
import json
from main import controller


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
            SYMBOL: [MessageHandler(Filters.regex("^[a-zA-Z]+$"), symbol_func)],
            PRICE: [MessageHandler(Filters.regex('^[0-9]+$'), price_func)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)
    updater.start_polling()
    updater.idle()


def start_cmd(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to stock ticker bot, "
                                                                    "please enter stock symbol")
    return SYMBOL


def symbol_func(update, context):
    global sym
    sym = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Enter price")
    return PRICE


def price_func(update, context):
    global thresh
    thresh = update.message.text
    curr = controller(sym, thresh)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Screener set for {sym} at {thresh}, "
                                                                    f"current price is {curr}")


def cancel(update, context):
    update.message.reply_text(
        'Bye! Ending Conversation.'
    )
    return ConversationHandler.END


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")