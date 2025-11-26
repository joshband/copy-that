"""Helpers to bootstrap a test database (Postgres or in-memory) with minimal seed data."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, StaticPool

from copy_that.domain.models import Base, ExtractionSession, Project, TokenLibrary


async def create_engine_from_env() -> AsyncEngine:
    """Create an async engine from TEST_DATABASE_URL or use in-memory SQLite."""
    db_url = os.getenv("TEST_DATABASE_URL")
    if db_url:
        return create_async_engine(db_url, poolclass=NullPool, echo=False)
    # default to in-memory sqlite
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )


async def prepare_db(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create all tables and return a sessionmaker."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_minimal(session: AsyncSession) -> None:
    """Seed minimal data required by API tests."""
    project = Project(name="Test Project", description="Seeded project for API tests")
    project2 = Project(name="Another Project", description="Second seeded project")
    session.add_all([project, project2])
    await session.commit()
    await session.refresh(project)
    await session.refresh(project2)

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


async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager-ish helper to yield a seeded session and clean up."""
    engine = await create_engine_from_env()
    SessionLocal = await prepare_db(engine)
    async with SessionLocal() as session:
        await seed_minimal(session)
        yield session
    await engine.dispose()
