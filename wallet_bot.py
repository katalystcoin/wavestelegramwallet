import requests
import config_dev as config
import telepot
from textwrap import dedent

from models.User import User

from telepot.exception import TelegramError

bot = telepot.Bot(config.bot_token) # TODO: Setup environment switching based on env var using zappa env var injection

def receive_message(msg):
    """Receive a raw message from Telegram"""
    print(msg)
    try:
        message = str(msg["message"]["text"])
        chat_id = msg["message"]["chat"]["id"]
        user_id = msg["message"]["from"]["id"]
        return message, chat_id, user_id
    except Exception as e:
        print(e)
        return (None, None)
 
def handle_message(message, chat_id, from_user_id):
    """Calculate a response to the message"""
    print(message.split())
    message_tokens = message.split()
    command = message_tokens[0]
    if command == '/help':
        response = dedent("""
        My supported commands are:
         /help
            Sends this message
         /register
            If you're a new user use this command to register
         /address
            Shows you your wallet address
         /sendWaves [recipient address] [number of waves]
            Sends [number of waves] to [recipient address].
        """)
    elif command == '/register':
        send_message(chat_id, "Registering a new wallet for you... Please wait.")
        try:
            user = User.retrieve(from_user_id)
            send_message(chat_id, "You already have an existing wallet!")
        except KeyError:
            user = User(from_user_id)
            user.save()
            response = 'Wallet registered! Your wallet address is: {}'.format(user.wallet.address)
    
    elif command == '/address':
        try:
            user = User.retrieve(from_user_id)
            response = 'Your wallet address is: {}'.format(user.wallet.address)
        except KeyError:
            response = "You don't have a wallet registered, use /register to make one"

    elif command == '/balance':
        try:
            user =  User.retrieve(from_user_id)
            response = "Your wallet WAVES balance is: {}".format(user.wallet.balance())
        except KeyError as e:
            response = "You don't have a wallet registered, use /register to make one"

    elif command == '/sendWaves':
        try:
            # user =  User.retrieve(from_user_id)
            response = "This feature has not been implemented yet, sorry!"
            # response = "Your wallet WAVES balance is: {}".format(user.wallet.balance())
        except KeyError as e:
            response = "You don't have a wallet registered, use /register to make one"

        except:
            response = "Something went wrong! Please try again later."

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