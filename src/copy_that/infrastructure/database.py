"""
Database configuration and session management
"""

import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Read DATABASE_URL from environment
# Default to local SQLite for development if not configured
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./copy_that.db")

# Convert postgresql:// to postgresql+asyncpg:// for async support
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Fix DATABASE_URL for asyncpg: remove sslmode parameter (not recognized by asyncpg)
# asyncpg handles SSL via ssl=True in connect_kwargs
engine_kwargs: dict[str, Any] = {
    "echo": os.getenv("ENVIRONMENT") == "local",  # Log SQL in development
    "pool_pre_ping": True,  # Verify connections before using
}

if "sqlite" not in DATABASE_URL:
    # PostgreSQL with asyncpg - remove sslmode parameter (not recognized by asyncpg)
    # and add SSL via connect_args instead
    if "sslmode=" in DATABASE_URL:
        # Properly parse URL and remove only sslmode while preserving other params
        parsed = urlparse(DATABASE_URL)
        query_params = parse_qs(parsed.query)
        # Remove sslmode parameter
        query_params.pop("sslmode", None)
        # Rebuild URL with remaining parameters
        new_query = urlencode(query_params, doseq=True)
        DATABASE_URL = urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
        )

    # Only enable SSL for non-localhost connections (cloud databases)
    # Localhost PostgreSQL typically doesn't support SSL
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        engine_kwargs["connect_args"] = {"ssl": True}

    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 1800  # Recycle connections after 30 minutes
    engine_kwargs["pool_timeout"] = 30  # Wait up to 30s for connection

# Create async engine
engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class for all models
class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
