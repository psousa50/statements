#!/bin/bash

cd "$(dirname "$0")/.."

source .venv/bin/activate

export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Run Celery worker in the background
python -m celery -A app.celery_app worker --loglevel=info &
WORKER_PID=$!

# Run Celery beat in the foreground
python -m celery -A app.celery_app beat --loglevel=info &
BEAT_PID=$!

echo "Celery worker running with PID: $WORKER_PID"
echo "Celery beat running with PID: $BEAT_PID"
echo "Press CTRL+C to stop both processes"

# Handle termination
trap "kill $WORKER_PID $BEAT_PID; exit" INT TERM

# Wait for both processes
wait