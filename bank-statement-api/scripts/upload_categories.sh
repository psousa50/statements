#!/bin/bash

curl -X POST "http://localhost:8000/categories/import" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/Users/pedrosousa/Work/Personal/statements/bank-statement-api/data/categories.csv"