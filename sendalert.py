from telegram import Bot
import json

with open("Telegram_token.json", "r") as f:
    api_key = json.load(f)
bot = Bot(token=api_key["key"])


def send_alert(id: int, sym: str, price: int, curr: int):
    if sym[:3] == "BSE":
        currency = "₹"
    else:
        currency = "$"
    bot.send_message(chat_id=id, text=f"Alert!\n{sym} triggered at {price}{currency}\ncurrent price: {curr}{currency}")
