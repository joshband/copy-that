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

try:  # Prefer real dependency, but allow offline shims for targeted unit tests.
    import pytest_asyncio  # type: ignore
except Exception:  # pragma: no cover - fallback when dependency is unavailable
    import types

    pytest_asyncio = types.SimpleNamespace(fixture=pytest.fixture)  # type: ignore

try:
    from httpx import AsyncClient
except Exception:  # pragma: no cover - allow running narrow unit slices without httpx

    class AsyncClient:  # type: ignore[no-redef]
        ...


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
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

_db_available = True
_db_import_error: Exception | None = None
try:
    import copy_that.infrastructure.persistence.models  # noqa: F401
    from copy_that.infrastructure.database import Base
    from copy_that.infrastructure.persistence.models import ExtractionSession, Project, TokenLibrary
    from copy_that.infrastructure.security.rate_limiter import reset_rate_limiter
    from copy_that.interfaces.api.main import app
except Exception as exc:  # pragma: no cover - allow running limited unit slices offline
    _db_available = False
    _db_import_error = exc

    def reset_rate_limiter() -> None:  # type: ignore[no-redef]
        return None


def pytest_configure(config):
    """Ensure pytest-asyncio runs in auto mode to avoid nested loop errors."""
    config.option.asyncio_mode = "auto"


@pytest.fixture(autouse=True)
def reset_rate_limiter_fixture():
    """Reset rate limiter state before each test to prevent 429 errors."""
    reset_rate_limiter()
    yield
    reset_rate_limiter()


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
    if not _db_available:
        pytest.skip(f"Database dependencies unavailable: {_db_import_error}")

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
        # Seed projects
        project = Project(name="Test Project", description="Seeded project for API tests")
        project2 = Project(name="Another Project", description="Second seeded project")
        session.add_all([project, project2])
        await session.commit()
        await session.refresh(project)
        await session.refresh(project2)

        # Seed a default session and library for the first project
        session_obj = ExtractionSession(
            project_id=project.id,
            name="Default Session",
            description="Seeded session for API tests",
        )
        session.add(session_obj)
        await session.flush()
        library = TokenLibrary(session_id=session_obj.id, token_type="color", statistics=None)
        session.add(library)
        await session.commit()
        await session.refresh(session_obj)
        await session.refresh(library)

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

    if not _db_available:
        pytest.skip(f"Database dependencies unavailable: {_db_import_error}")

    # Override the database dependency
    async def override_get_db():
        yield test_db

    try:
        from httpx import ASGITransport
    except Exception:  # pragma: no cover - offline shim

        class ASGITransport:  # type: ignore
            def __init__(self, *args, **kwargs):
                raise RuntimeError("httpx is required for async_client fixture")

    from copy_that.infrastructure.database import get_db

    previous_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Restore overrides to avoid breaking pre-wired app dependencies.
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous_overrides)


@pytest.fixture
def mock_api_key(monkeypatch):
    """
    Set a mock ANTHROPIC_API_KEY for testing without real API calls.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-sk-proj-123456789")
    return "test-key-sk-proj-123456789"
