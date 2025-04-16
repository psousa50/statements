#!/bin/bash

FILE=$1
API_URL="http://localhost:8000/transactions/analyze"

if [ -z "$FILE" ]; then
  FILE="/Users/pedrosousa/Work/Personal/statements/tmp/revolut.csv"
fi

if [ ! -f "$FILE" ]; then
  echo "File not found: $FILE"
  exit 1
fi

FILE_NAME=$(basename "$FILE")
BASE64_CONTENT=$(base64 -i"$FILE" | tr -d '\n')

JSON_PAYLOAD=$(jq -n \
  --arg file_content "$BASE64_CONTENT" \
  --arg file_name "$FILE_NAME" \
  '{file_content: $file_content, file_name: $file_name}'
)

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD"