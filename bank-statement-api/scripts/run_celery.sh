#!/bin/bash

# Change to the project directory
cd "$(dirname "$0")/.."

# Activate the virtual environment
source .venv/bin/activate

# Export the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Start Celery worker
python -m celery -A app.celery_app worker --loglevel=info
