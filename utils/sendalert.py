from telegram import Bot
import json
import os
from utils import initlogger

logger = initlogger.getloggerobj(os.path.basename(__file__))

with open("./config/Telegram_token.json", "r") as f:
    api_key = json.load(f)
bot = Bot(token=api_key["key"])


def send_alert(chatid: int, sym: str, price: int, curr: int):
    logger.debug(f"Exchange: {sym[:3]}")
    if sym[:3] == "BSE":
        currency = "₹"
    else:
        currency = "$"
    bot.send_message(chat_id=chatid, text=f"⚠️Alert!\n{sym} triggered at {price}{currency}\ncurrent price: {curr}{currency}")
