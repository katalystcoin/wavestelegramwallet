from textwrap import dedent
import telepot
from config import config
import pywaves

from models.User import User

from telepot.exception import TelegramError

import traceback

WAVES_DECIMALS = 10e7

bot = telepot.Bot(
    config.BOT_TOKEN
)
pywaves.setThrowOnError(True)


def receive_message(msg):
    """Receive a raw message from Telegram"""
    print(msg)
    try:
        message = str(msg["message"]["text"])
        chat_id = msg["message"]["chat"]["id"]
        user_id = msg["message"]["from"]["id"]
        return message, chat_id, user_id
    except Exception as e:
        print(traceback.format_exc())
        print("errored")

def handle_message(message, chat_id, from_user_id):
    """Calculate a response to the message"""
    print(message.split())
    message_tokens = message.split()
    command = message_tokens[0]
    if command == "/help":
        response = dedent(
            """
        My supported commands are:
         /help
            Sends this message
         /register
            If you're a new user use this command to register
         /address
            Shows you your wallet address
         /balance
            Shows you your wallet's Waves balance
         /sendWaves [recipient address] [number of waves]
            Sends [number of waves] to [recipient address].
        """
        )
    elif command == "/register":
        send_message(
            chat_id, "Registering a new wallet for you... Please wait.")
        try:
            user = User.retrieve(from_user_id)
            send_message(chat_id, "You already have an existing wallet!")
        except KeyError:
            user = User(from_user_id)
            response = "Wallet registered! Your wallet address is: {}".format(
                user.wallet.address
            )

    elif command == "/address":
        try:
            user = User.retrieve(from_user_id)
            response = "Your wallet address is: {}".format(user.wallet.address)
        except KeyError:
            response = "You don't have a wallet registered, use /register to make one"

    elif command == "/balance":
        try:
            user = User.retrieve(from_user_id)
            balance = str(float(user.wallet.balance()) / WAVES_DECIMALS) 
            response = "Your wallet WAVES balance is: {}".format(balance)
        except KeyError as e:
            response = "You don't have a wallet registered, use /register to make one"

    elif command == "/sendWaves":
        try:
            if len(message_tokens) < 3:
                raise ValueError("Insufficient arguments")
            user =  User.retrieve(from_user_id)
            recipient = pywaves.Address(message_tokens[1]) # TODO: Abstract this out from this file
            amount = int(float(message_tokens[2]) * WAVES_DECIMALS)
            user.wallet.sendWaves(recipient, amount)
            response = "Transaction sent! It may take a few minutes for the change in your balance to take effect. You can check your balance with /balance"
        except KeyError as e:
            response = "You don't have a wallet registered, use /register to make one"
        except pywaves.PyWavesException as e:
            response = e.args[0]
        except ValueError as e:
            if e.args[0] == "Invalid address":
                response = "Invalid recipient address, please check that it is correct"
            elif e.args[0] == "Insufficient arguments":
                response = "/sendWaves requires a recipient address and an amount to send, please check your command"
            elif "could not convert string to float" in e.args[0]:
                response = "/sendWaves requires a numerical amount to send, note that the brackets are to be omitted"
            else:
                response = "Something went wrong! Please check your command"
        except:
            response = "Something went wrong! Please try again later."
            raise

    elif command == "/version":
        response = "Version is 0.0.4"

    else:
        response = "Unknown command, try /help"
    return response


def send_message(chat_id, message):
    bot.sendMessage(chat_id, text=message, parse_mode="html")


def run(message):
    """Receive a message, handle it, and send a response"""
    try:
        message, chat_id, from_user_id = receive_message(message)
        response = handle_message(message, chat_id, from_user_id)
        send_message(chat_id, response)
    except Exception as e:
        print(e)
