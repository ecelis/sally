#!/bin/bash

CWD="$(dirname $(readlink -f $0))"
cd $CWD
. $CWD/env.sh
$CWD/ENV/bin/python $CWD/cron.py
