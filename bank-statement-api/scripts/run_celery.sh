#!/bin/bash

cd "$(dirname "$0")/.."

source .venv/bin/activate

export PYTHONPATH=$PYTHONPATH:$(pwd)/src

python -m celery -A app.celery_app worker --loglevel=info
