#!/bin/bash

SPIDER=$1
URLS=$2

usage() {
  echo "Usage $0 <crawler> -a csvfile=<source.csv>"
  echo "Available spiders:"
  echo `ls sally/spiders/*_spider.py | cut -d'/' -f3 | cut -d'_' -f1`
  echo
  exit 1
}

[[ $# -eq 0 ]] && usage

. ./env.sh
if [ -z $URLS ]
then
  scrapy crawl $SPIDER
else
  scrapy crawl $SPIDER -a "csvfile=$URLS"
fi
