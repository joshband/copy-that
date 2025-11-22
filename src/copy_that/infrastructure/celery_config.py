import os
import time
from urllib.parse import urlparse

import redis
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Redis URL from environment
redis_url = os.getenv("CELERY_BROKER_URL")
result_backend_url = os.getenv("CELERY_RESULT_BACKEND")

# Parse Redis URL for Upstash
parsed_url = urlparse(redis_url)

# Determine if using Upstash (requires SSL) or local Redis (no SSL)
is_upstash = parsed_url.hostname and "upstash" in parsed_url.hostname

# Construct Redis configuration
redis_config = {
    "host": parsed_url.hostname,
    "port": parsed_url.port,
    "username": parsed_url.username or "default",
    "password": parsed_url.password,
    "ssl": is_upstash,  # Only enable SSL for Upstash
    "ssl_cert_reqs": None if is_upstash else None,  # Disable SSL verification for Upstash
    "socket_timeout": 10,
    "socket_connect_timeout": 5,
    "retry_on_timeout": True,
    "max_connections": 10,
}

# Create Celery app
app = Celery("copy_that", broker=redis_url, backend=result_backend_url)

# Celery configuration
app.conf.update(
    broker_url=redis_url,
    result_backend=result_backend_url,
    # Use JSON for serialization
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    # Timezone
    timezone="UTC",
    # Enable task error reporting
    task_track_started=True,
    task_send_sent_event=True,
    # Retry configuration
    task_retry_max_retries=3,
    # Disable prefetching to prevent long-running tasks blocking others
    worker_prefetch_multiplier=1,
    # Redis connection settings
    redis_backend_health_check_interval=4,
    redis_socket_timeout=10,
    # Broker connection settings
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=3,
)


# Experimental connection handling
def robust_redis_connection(max_retries=3):
    for attempt in range(max_retries):
        try:
            r = redis.Redis(**redis_config)
            r.ping()
            return r
        except Exception as e:
            print(f"Redis connection attempt {attempt + 1} failed: {e}")
            time.sleep(2**attempt)  # Exponential backoff
    return None


# Example task for testing
@app.task(bind=True, max_retries=3)
def test_task(self, x, y):
    try:
        result = x + y
        return result
    except Exception as exc:
        # Retry the task with exponential backoff
        self.retry(exc=exc, countdown=2**self.request.retries)


# Health check task
@app.task(bind=True)
def health_check(self):
    return "Celery task queue is operational!"


# Experimental health check with direct Redis connection
def test_redis_connection():
    try:
        r = robust_redis_connection()
        return r is not None
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False
