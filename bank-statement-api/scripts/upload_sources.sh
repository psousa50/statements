#!/bin/bash

curl -X POST "http://localhost:8000/sources/import" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/Users/pedrosousa/Work/Personal/statements/bank-statement-api/data/sources.csv"
