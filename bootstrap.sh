#!/bin/sh

python3 -m venv ENV
. ENV/bin/activate
pip3 install --upgrade pip
pip install -r requirements.txt
python google/authorize.py --noauth_local_webserver
