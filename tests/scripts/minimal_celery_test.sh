#!/bin/bash
set -ex

# Start Celery worker
celery -A minimal_celery_test worker --loglevel=INFO &
CELERY_PID=$!

# Wait briefly for the worker to start
sleep 2

# Run the test script
python3 minimal_celery_test.py

# Kill the Celery worker
kill $CELERY_PID

# Wait for the worker to exit
wait $CELERY_PID || true
