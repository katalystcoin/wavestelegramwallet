#!/bin/bash

python -m deploy.py
python -m initialize_db.py
zappa update dev