import sys
import requests
from config import config
import boto3
import slugify
import aws_utils

TELEGRAM_API = "https://api.telegram.org/bot{}".format(config.BOT_TOKEN)
SET_WEBHOOK_PATH = TELEGRAM_API + "/setWebhook?url={}".format(aws_utils.get_api_url())
print(requests.get(SET_WEBHOOK_PATH))
