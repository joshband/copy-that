#!/bin/bash
set -ex

# Print versions
echo "Python Version:"
python3 --version

echo "Celery Version:"
celery --version

# Verify Redis is running
redis-cli ping

# Start Celery worker
celery -A celery_diagnostics worker --loglevel=INFO &
CELERY_PID=$!

# Wait briefly for the worker to start
sleep 3

# Run the diagnostics script
python3 celery_diagnostics.py

# Kill the Celery worker
kill $CELERY_PID

# Wait for the worker to exit
wait $CELERY_PID || true
