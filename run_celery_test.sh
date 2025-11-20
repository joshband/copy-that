#!/bin/bash
set -ex

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Print Python and Celery versions
python3 --version
celery --version

# Start Celery worker in the background with minimal logging
celery -A src.copy_that.infrastructure.celery_config worker --loglevel=ERROR &
CELERY_PID=$!

# Wait briefly for the worker to start
sleep 2

# Run the test script with timeout
timeout 30 python3 test_celery_queue.py

# Kill the Celery worker
kill $CELERY_PID

# Wait for the worker to exit
wait $CELERY_PID || true