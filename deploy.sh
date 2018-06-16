#!/bin/bash

python -m deploy.py
python -m initialize_db.py
python -m update.py
python -m set_webhook.py