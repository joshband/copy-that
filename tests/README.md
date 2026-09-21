# Tests and Scripts

- Main test suite: `tests/` (pytest).
- Helper scripts (moved from root): `tests/scripts/`:
  - `test_celery_queue.py`
  - `test_color_extraction.py`
  - `test_e2e_session5.py`
  - `test_performance_50_images.py`
  - `test_redis_connection.py`

Usage:
- Run targeted scripts directly (`python tests/scripts/test_color_extraction.py`) when you need quick checks; prefer `pytest` for full coverage.
