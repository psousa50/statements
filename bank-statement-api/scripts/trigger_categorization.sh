#!/bin/bash

cd "$(dirname "$0")/.."

source .venv/bin/activate

export PYTHONPATH=$PYTHONPATH:$(pwd)/src

curl -X POST "http://localhost:8000/categorization/process-now" -H "accept: application/json"