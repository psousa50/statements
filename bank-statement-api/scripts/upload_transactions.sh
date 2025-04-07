#!/bin/bash

curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/Users/pedrosousa/Work/Personal/statements/tmp/revolut.csv"