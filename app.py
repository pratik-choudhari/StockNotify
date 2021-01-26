import os
from config.configkeys import config_keys
os.environ['KEY_FOUND'] = 'False'


alpha_path = r"./config/alpha_vantage_api_key.json"
telegram_path = r"./config/Telegram_token.json"

if not (os.path.exists(alpha_path) and os.path.exists(telegram_path)):
    print("Missing API keys:\n1.alpha_vantage_api_key.json\n2.Telegram_token.json\nin config dir")
else:
    config_keys['KEY_FOUND'] = 'True'
    try:
        from utils import main
    except Exception as e:
        print(e)
    else:
        main.telegrambot()
