"""
Playwright configuration for UI testing
"""

# Configuration for pytest-playwright
# Run tests with: pytest tests/ui/ --browser chromium

# Default settings
PLAYWRIGHT_BROWSER = "chromium"
PLAYWRIGHT_HEADLESS = True
PLAYWRIGHT_SLOW_MO = 0  # Set to 100 for debugging

# Base URL for tests
BASE_URL = "http://localhost:8000"

# Screenshot settings
SCREENSHOT_ON_FAILURE = True
SCREENSHOT_DIR = "test-results/screenshots"

# Video recording
VIDEO_ON_FAILURE = True
VIDEO_DIR = "test-results/videos"
