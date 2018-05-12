from flask import Flask
from flask import request
from wallet_bot import run

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def receive():
    try:
        run(request.json)
        return ""
    except Exception as e:
        print(e)
        return ""

# For local development purposes
# > export FLASK_APP=bot_server.py
# > flask run
if __name__ == '__main__':
   app.run()