import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.copy_that.infrastructure.celery_config import (
    health_check,
    robust_redis_connection,
    test_task,
)


def main():
    print("Testing Celery and Redis Configuration...\n")

    # Test Redis connection with shorter timeout
    print("0. Redis Connection:")
    try:
        r = robust_redis_connection(max_retries=1)
        if r:
            r.ping()
            print("Redis Connection: ✓ SUCCESS")
        else:
            print("Redis Connection: ✗ FAILED")
            return
    except Exception as e:
        print(f"Redis connection error: {e}")
        return

    # Test Celery health check task with shorter timeout
    print("\n1. Celery Health Check Task:")
    try:
        health_result = health_check.apply_async()
        result = health_result.get(timeout=5)
        print(f"Health check result: {result}")
        print(f"Task state: {health_result.state}")
    except Exception as e:
        print(f"Health check task failed: {type(e).__name__}: {e}")

    # Test simple addition task
    print("\n2. Test Addition Task:")
    try:
        task = test_task.apply_async(args=[5, 3])
        result = task.get(timeout=5)
        print(f"Task result: 5 + 3 = {result}")
        print(f"Task state: {task.state}")
    except Exception as e:
        print(f"Addition task failed: {type(e).__name__}: {e}")

    print("\nCelery queue testing completed.")


if __name__ == "__main__":
    main()
