"""
Pytest configuration and shared fixtures for all tests

This module:
1. Sets up PYTHONPATH for imports from src/
2. Provides database fixtures for testing
3. Provides FastAPI test client fixtures
4. Provides async session fixtures
"""

import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

# Skip collection of legacy pipeline suites (deprecated and slated for removal)
collect_ignore = [
    "unit/pipeline",
    "integration/test_pipeline_integration.py",
    "unit/test_color_pipeline_comprehensive.py",
    "token_smoke_test.py",
]

# Add src directory to path so imports work
root_path = Path(__file__).parent.parent
src_path = root_path / "src"
tests_path = root_path / "tests"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(tests_path))

# Avoid loading local .env during test runs (can contain unparsable dev secrets)
os.environ.setdefault("PYTHON_DOTENV_IGNORE_ENV_FILE", "1")

# Now import our modules
# Import all models to register them with Base.metadata
# This must happen BEFORE calling Base.metadata.create_all()
import copy_that.domain.models  # noqa: F401
from copy_that.domain.models import Base
from copy_that.interfaces.api.main import app
from tests.utils.test_db import create_engine_from_env, prepare_db, seed_minimal


def pytest_configure(config):
    """Ensure pytest-asyncio runs in auto mode to avoid nested loop errors."""
    config.option.asyncio_mode = "auto"


@pytest_asyncio.fixture
async def test_db():
    """
    Create an in-memory SQLite database for testing.

    This fixture:
    - Creates a fresh database for each test
    - Creates all tables
    - Yields the session
    - Cleans up after the test
    """
    # Respect TEST_DATABASE_URL if set; otherwise use in-memory SQLite
    if os.getenv("TEST_DATABASE_URL"):
        engine = await create_engine_from_env()
        SessionLocal = await prepare_db(engine)
        async with SessionLocal() as session:
            await seed_minimal(session)
            yield session
        await engine.dispose()
    else:
        # In-memory SQLite fallback
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        from sqlalchemy.ext.asyncio import async_sessionmaker

        TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with TestSessionLocal() as session:
            await seed_minimal(session)
            yield session

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        await engine.dispose()


@pytest_asyncio.fixture
async def async_client(test_db):
    """
    Create an async HTTP client for testing FastAPI endpoints.

    This fixture:
    - Patches the database dependency to use the test database
    - Provides an AsyncClient for making requests
    """

    # Override the database dependency
    async def override_get_db():
        yield test_db

    from httpx import ASGITransport

    from copy_that.infrastructure.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_api_key(monkeypatch):
    """
    Set a mock ANTHROPIC_API_KEY for testing without real API calls.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-sk-proj-123456789")
    return "test-key-sk-proj-123456789"
