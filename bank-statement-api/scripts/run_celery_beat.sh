#!/bin/bash

# Change to the project directory
cd "$(dirname "$0")/.."

# Activate the virtual environment
source .venv/bin/activate

# Export the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Start Celery beat scheduler
python -m celery -A app.celery_app beat --loglevel=info
