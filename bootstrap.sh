#!/bin/sh

python3 -m venv ENV
. ENV/bin/activate
pip3 install --upgrade pip
pip install -r requirements.txt
# Auth will fail within VM since client_secret.json is missing
python google/authorize.py --noauth_local_webserver
