#!/bin/sh

export PATH=.:$PATH
for i in `cat variables.env`; do
  export $i
done

. ENV/bin/activate
