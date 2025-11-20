from celery import Celery
import os
import sys
import traceback

# Explicitly print Python and Celery paths
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print(f"Celery Version: {Celery.__version__ if hasattr(Celery, '__version__') else 'Unknown'}")
print(f"Current Working Directory: {os.getcwd()}")

# Create Celery app with verbose configuration
app = Celery('celery_diagnostics',
             broker='redis://localhost:6379/1',
             backend='redis://localhost:6379/2')

# Detailed configuration
app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_routes={
        'celery_diagnostics.debug_task': {'queue': 'debug'}
    },
    task_annotations={
        'celery_diagnostics.debug_task': {'rate_limit': '10/m'}
    }
)

@app.task(name='celery_diagnostics.debug_task')
def debug_task(x, y):
    print(f"Debug task executed with arguments: {x}, {y}")
    return x + y

def main():
    try:
        print("\n--- Registering Tasks ---")
        # List all registered tasks
        print("Registered Tasks:", list(app.tasks.keys()))

        print("\n--- Sending Task ---")
        result = app.send_task('celery_diagnostics.debug_task', args=[5, 3])
        print(f"Task ID: {result.id}")

        print("\n--- Retrieving Task Result ---")
        task_result = result.get()
        print(f"Task Result: {task_result}")

    except Exception as e:
        print("\n--- Error Details ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    main()