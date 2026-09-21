import os
from urllib.parse import urlparse

import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Redis URL from environment
redis_url = os.getenv("REDIS_URL")

try:
    # Parse the URL
    parsed_url = urlparse(redis_url)

    # Create Redis client with correct SSL settings
    r = redis.Redis(
        host=parsed_url.hostname,
        port=parsed_url.port,
        username=parsed_url.username or "default",
        password=parsed_url.password,
        ssl=True,
        ssl_cert_reqs=None,  # Disable SSL verification for Upstash
    )

    # Test connection by pinging
    response = r.ping()
    print(f"Redis connection successful! Ping response: {response}")

    # Set and get a test key
    test_key = "copy_that_test"
    test_value = "connection_works"

    r.set(test_key, test_value)
    retrieved_value = r.get(test_key)

    print("Test key set and retrieved successfully.")
    print(f"Set: {test_key} = {test_value}")
    print(f"Retrieved: {test_key} = {retrieved_value.decode('utf-8')}")

    # Clean up test key
    r.delete(test_key)

except Exception as e:
    print(f"Redis connection failed: {e}")
    import traceback

    traceback.print_exc()
