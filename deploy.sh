#!/bin/bash

python deploy.py
python initialize_db.py
python update.py
python set_webhook.py