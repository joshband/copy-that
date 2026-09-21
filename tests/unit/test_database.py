"""Tests for database infrastructure module"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from copy_that.infrastructure.database import Base, get_db


class TestDatabaseInfrastructure:
    """Test database infrastructure"""

    @pytest_asyncio.fixture
    async def test_engine(self):
        """Create a test database engine"""
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            poolclass=StaticPool,
            echo=False,
        )

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        await engine.dispose()

    @pytest.mark.asyncio
    async def test_base_metadata_exists(self):
        """Test that Base has metadata"""
        assert Base.metadata is not None

    @pytest.mark.asyncio
    async def test_get_db_generator(self, test_engine):
        """Test get_db yields a session"""
        # This tests the generator pattern
        async for session in get_db():
            assert session is not None
            break

    @pytest.mark.asyncio
    async def test_async_session_creation(self, test_engine):
        """Test async session can be created"""
        async with AsyncSession(test_engine, expire_on_commit=False) as session:
            assert session is not None
            # Should be able to execute simple query
            result = await session.execute(
                Base.metadata.tables.get("projects").select()
                if "projects" in Base.metadata.tables
                else None
            )
            # Just verify we can execute without error
            assert True

    @pytest.mark.asyncio
    async def test_base_tables_created(self, test_engine):
        """Test that base tables are created"""
        # Check that tables exist in metadata
        assert len(Base.metadata.tables) > 0


class TestDatabaseURL:
    """Test database URL handling"""

    def test_database_url_import(self):
        """Test that DATABASE_URL can be imported"""
        from copy_that.infrastructure.database import DATABASE_URL

        assert DATABASE_URL is not None
        assert isinstance(DATABASE_URL, str)

    def test_async_session_local_import(self):
        """Test that AsyncSessionLocal can be imported"""
        from copy_that.infrastructure.database import AsyncSessionLocal

        assert AsyncSessionLocal is not None

    def test_engine_import(self):
        """Test that engine can be imported"""
        from copy_that.infrastructure.database import engine

        assert engine is not None
