import requests
import config_dev
import sys

TELEGRAM_API = "https://api.telegram.org/bot{}".format(config_dev.bot_token) # TODO: Setup environment switching like in other
SET_WEBHOOK_PATH = TELEGRAM_API + "/setWebhook?url={}".format(sys.argv[1])
print(requests.get(SET_WEBHOOK_PATH))