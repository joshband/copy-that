"""Lightweight pytest-asyncio shim for environments without the dependency.

This stub is only intended to allow unit tests that do not rely on real
asyncio features to import `pytest_asyncio.fixture`. It defers to pytest's
native fixture decorator.
"""

import pytest

fixture = pytest.fixture

__all__ = ["fixture"]
