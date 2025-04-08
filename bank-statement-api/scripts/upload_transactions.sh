#!/bin/bash

FILE=$1

if [ -z "$FILE" ]; then
  FILE="/Users/pedrosousa/Work/Personal/statements/tmp/revolut.csv"
fi

curl -X POST "http://localhost:8000/transactions/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$FILE"