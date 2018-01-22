#!/bin/bash

echo "$(dirname $(readlink -f $0))"
cd /home/ecelis/Projects/sally
. ./env.sh
python cron.py
