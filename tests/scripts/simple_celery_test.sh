#!/bin/bash
set -ex

# Start Celery worker in the background
celery -A simple_celery_test worker --loglevel=INFO &
CELERY_PID=$!

# Wait a moment for the worker to start
sleep 2

# Run the test script
python3 simple_celery_test.py

# Kill the Celery worker
kill $CELERY_PID

# Wait for the worker to exit
wait $CELERY_PID || true