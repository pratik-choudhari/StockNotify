import os
import json
from telegram import Bot

from utils import initlogger

logger = initlogger.getloggerobj(os.path.basename(__file__))

with open("./config/Telegram_token.json", "r") as f:
    api_key = json.load(f)
bot = Bot(token=api_key["key"])


def send_alert(chatid: int, sym: str, price: int, curr: int):
    logger.info(f"Triggered: {sym} at {price} for {chatid}")
    bot.send_message(chat_id=chatid, text=f"⚠️Alert!\n{sym} triggered at {price}\ncurrent price: {curr}")
