import json
from telegram.ext import Updater, CommandHandler, ConversationHandler


def telegrambot():
    with open("../config/Telegram_token.json", "r") as f:
        api_key = json.load(f)

    updater = Updater(token=api_key["key"], use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('/start', start_cmd)
    dispatcher.add_handler(start_handler)
    updater.start_polling()
    updater.idle()


def start_cmd(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Test message.")
    return ConversationHandler.END


if __name__ == "__main__":
    telegrambot()
