#!/bin/bash
pipenv shell
export FLASK_APP=bot_server.py
export FLASK_DEBUG=1
flask run
