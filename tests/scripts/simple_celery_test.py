import os

from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Redis URL from environment
redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
result_backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# Create Celery app
app = Celery(
    "simple_celery_test",
    broker=redis_url,
    backend=result_backend_url,
    include=["simple_celery_test"],
)

# Configure Celery
app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)


# Simple task
@app.task(bind=True, name="simple_celery_test.add")
def add(self, x, y):
    print(f"Executing task {self.request.id}")
    return x + y


def main():
    print(f"Broker URL: {redis_url}")
    print(f"Result Backend URL: {result_backend_url}")

    result = app.send_task("simple_celery_test.add", args=[4, 4])
    print(f"Task ID: {result.id}")
    print(f"Result: {result.get()}")


if __name__ == "__main__":
    main()
