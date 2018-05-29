import sys
import requests
from config import config

TELEGRAM_API = "https://api.telegram.org/bot{}".format(config.BOT_TOKEN)
SET_WEBHOOK_PATH = TELEGRAM_API + "/setWebhook?url={}".format(sys.argv[1])
print(requests.get(SET_WEBHOOK_PATH))
