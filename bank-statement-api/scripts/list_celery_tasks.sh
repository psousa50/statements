#!/bin/bash

cd "$(dirname "$0")/.."

source .venv/bin/activate

export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# List scheduled tasks
echo "=== Scheduled Tasks ==="
python -m celery -A app.celery_app inspect scheduled

# List active tasks
echo -e "\n=== Active Tasks ==="
python -m celery -A app.celery_app inspect active

# List reserved tasks (tasks that have been received but not yet executed)
echo -e "\n=== Reserved Tasks ==="
python -m celery -A app.celery_app inspect reserved

# Show registered tasks
echo -e "\n=== Registered Tasks ==="
python -m celery -A app.celery_app inspect registered
