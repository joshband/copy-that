"""Load testing for Copy That API.

Run with:
    locust -f tests/load/locustfile.py --headless -u 100 -r 10 -t 1m

Or with web UI:
    locust -f tests/load/locustfile.py
    # Then open http://localhost:8089
"""

import os

from locust import HttpUser, between, task


class CopyThatUser(HttpUser):
    """Simulates a typical user of the Copy That API."""

    # Wait between 1-3 seconds between tasks
    wait_time = between(1, 3)

    # Base URL - override with --host flag
    host = os.getenv("API_URL", "http://localhost:8000")

    def on_start(self):
        """Called when a simulated user starts."""
        # Login and get token (if auth is enabled)
        # self.token = self.login()
        pass

    @task(3)
    def health_check(self):
        """Check API health - highest frequency."""
        self.client.get("/health")

    @task(2)
    def list_projects(self):
        """List user projects."""
        self.client.get("/api/v1/projects")

    @task(2)
    def list_libraries(self):
        """List token libraries."""
        self.client.get("/api/v1/libraries")

    @task(1)
    def get_project_tokens(self):
        """Get tokens for a project - moderate frequency."""
        # In real test, use actual project ID
        self.client.get("/api/v1/projects/test-project/tokens")

    @task(1)
    def export_tokens(self):
        """Export tokens to different formats."""
        formats = ["css", "w3c", "react"]
        for fmt in formats:
            self.client.get(
                f"/api/v1/export/{fmt}",
                params={"library_id": "test-library"},
                name=f"/api/v1/export/[format]",
            )


class ExtractorUser(HttpUser):
    """Simulates users performing token extraction - heavier load."""

    wait_time = between(3, 8)
    host = os.getenv("API_URL", "http://localhost:8000")

    @task
    def extract_colors(self):
        """Submit image for color extraction."""
        # This would normally upload an image
        self.client.post(
            "/api/v1/extract/colors",
            json={
                "image_url": "https://example.com/test-image.png",
                "options": {"min_confidence": 0.7},
            },
        )


# Performance thresholds for CI
# These will cause locust to exit with error if exceeded
if os.getenv("CI"):
    from locust import events

    @events.quitting.add_listener
    def check_fail_ratio(environment, **kwargs):
        """Fail if error rate > 1% or p99 > 500ms."""
        stats = environment.stats.total
        fail_ratio = stats.fail_ratio * 100

        if fail_ratio > 1:
            print(f"FAIL: Error rate {fail_ratio:.2f}% > 1%")
            environment.process_exit_code = 1

        if stats.get_response_time_percentile(0.99) > 500:
            p99 = stats.get_response_time_percentile(0.99)
            print(f"FAIL: p99 response time {p99}ms > 500ms")
            environment.process_exit_code = 1
