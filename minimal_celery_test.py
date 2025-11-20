import redis
from celery import Celery

# Establish Redis connection first
r = redis.Redis(host='localhost', port=6379)
print("Redis Connection Test:", r.ping())

# Create Celery app with minimal configuration
app = Celery('minimal_test', broker='redis://localhost:6379/1', backend='redis://localhost:6379/2')

@app.task
def add(x, y):
    print(f"Executing task with {x} and {y}")
    return x + y

if __name__ == '__main__':
    # Directly call the task without worker
    result = add.delay(4, 5)
    print("Task ID:", result.id)
    print("Result:", result.get())