"""
Pytest configuration and shared fixtures for all tests

This module:
1. Sets up PYTHONPATH for imports from src/
2. Provides database fixtures for testing
3. Provides FastAPI test client fixtures
4. Provides async session fixtures
"""

import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

# Add src directory to path so imports work
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Now import our modules
# Import all models to register them with Base.metadata
# This must happen BEFORE calling Base.metadata.create_all()
import copy_that.domain.models  # noqa: F401
from copy_that.infrastructure.database import Base
from copy_that.interfaces.api.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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
    # Use SQLite in-memory database for testing (much faster than PostgreSQL)
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    from sqlalchemy.ext.asyncio import async_sessionmaker

    TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with TestSessionLocal() as session:
        yield session

    # Cleanup
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
