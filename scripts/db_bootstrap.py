"""
Local database bootstrap for Copy That.

Postgres (recommended): run Alembic migrations against Docker Compose Postgres.
SQLite (smoke/dev): create schema from SQLAlchemy models and stamp Alembic head,
because several historical migrations use ALTER TABLE patterns SQLite cannot apply.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import dotenv_values, load_dotenv

load_dotenv(ROOT / ".env")


LOCAL_POSTGRES_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/copy_that"
LOCAL_SQLITE_URL = f"sqlite+aiosqlite:///{ROOT / 'copy_that_local.db'}"


def _normalize_url(url: str) -> str:
    return url.strip().strip('"').strip("'")


def _default_database_url() -> str:
    """Resolve default URL without being poisoned by leftover shell smoke URLs."""
    file_vals = dotenv_values(ROOT / ".env")
    file_url = (file_vals.get("DATABASE_URL") or "").strip()
    env_url = (os.getenv("DATABASE_URL") or "").strip()

    # Prefer .env file for bootstrap defaults; fall back to process env.
    candidate = _normalize_url(file_url or env_url or LOCAL_POSTGRES_URL)

    # Hosted Neon / leftover smoke SQLite → local Docker Postgres for offline bootstrap.
    if "neon.tech" in candidate or "copy_that_smoke" in candidate or candidate.endswith(
        "copy_that_local.db"
    ):
        if candidate != LOCAL_POSTGRES_URL:
            print(
                "Bootstrap defaulting to local Docker Postgres.\n"
                f"  (ignored: {candidate})\n"
                f"  using: {LOCAL_POSTGRES_URL}\n"
                "Pass --url to override."
            )
        return LOCAL_POSTGRES_URL
    return candidate


def dialect_of(url: str) -> str:
    parsed = urlparse(url)
    scheme = (parsed.scheme or "").split("+")[0].lower()
    if scheme.startswith("postgres"):
        return "postgresql"
    if scheme.startswith("sqlite"):
        return "sqlite"
    return scheme or "unknown"


def run_alembic(*args: str, database_url: str) -> None:
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    cmd = [sys.executable, "-m", "alembic", *args]
    print(f"+ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


async def sqlite_create_all(database_url: str) -> None:
    os.environ["DATABASE_URL"] = database_url
    # Import after env is set so the engine binds to this URL.
    from copy_that.infrastructure.database import Base, engine
    from copy_that.infrastructure.persistence import models  # noqa: F401

    # Quiet create_all; SQLAlchemy may inherit echo from env elsewhere.
    engine.sync_engine.echo = False  # type: ignore[attr-defined]
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


def wait_for_postgres(database_url: str, timeout_s: float = 60.0) -> None:
    """Poll Postgres until accepting connections."""
    # psycopg2 wants postgresql://… not postgresql+psycopg2://…
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    sync_url = sync_url.replace("postgresql+psycopg2://", "postgresql://", 1)
    import psycopg2

    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            conn = psycopg2.connect(sync_url)
            conn.close()
            print("Postgres is ready.")
            return
        except Exception as exc:  # noqa: BLE001 - intentional retry loop
            last_err = exc
            time.sleep(1.0)
    raise RuntimeError(f"Postgres did not become ready within {timeout_s}s: {last_err}")


def ensure_postgres_container() -> None:
    print("Starting local Postgres via Docker Compose...")
    subprocess.run(
        ["docker", "compose", "up", "-d", "postgres"],
        cwd=ROOT,
        check=True,
    )


def bootstrap(database_url: str, *, start_postgres: bool) -> None:
    dialect = dialect_of(database_url)
    print(f"Bootstrapping database ({dialect}): {database_url}")

    if dialect == "postgresql":
        if start_postgres:
            ensure_postgres_container()
        wait_for_postgres(database_url)
        run_alembic("upgrade", "head", database_url=database_url)
        print("Alembic upgrade head complete.")
        return

    if dialect == "sqlite":
        path = urlparse(database_url).path
        if path and path != ":memory:":
            db_path = Path(path)
            if db_path.exists():
                print(f"Removing existing SQLite file: {db_path}")
                db_path.unlink()
        print("SQLite path: create_all + alembic stamp head")
        asyncio.run(sqlite_create_all(database_url))
        run_alembic("stamp", "head", database_url=database_url)
        print("SQLite schema created and stamped at Alembic head.")
        return

    raise SystemExit(f"Unsupported DATABASE_URL dialect: {dialect}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap local Copy That database")
    parser.add_argument(
        "--url",
        default=None,
        help="Database URL (default: local Postgres, see script docstring)",
    )
    parser.add_argument(
        "--sqlite",
        action="store_true",
        help=f"Use local SQLite at {LOCAL_SQLITE_URL}",
    )
    parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Do not start Docker Compose Postgres (assume already running)",
    )
    parser.add_argument(
        "--wait-only",
        action="store_true",
        help="Only wait for Postgres readiness (no migrations)",
    )
    args = parser.parse_args()

    if args.sqlite:
        url = LOCAL_SQLITE_URL
    elif args.url:
        url = _normalize_url(args.url)
    else:
        url = _default_database_url()

    if args.wait_only:
        if dialect_of(url) != "postgresql":
            raise SystemExit("--wait-only only applies to Postgres URLs")
        if not args.no_docker:
            ensure_postgres_container()
        wait_for_postgres(url)
        return 0

    bootstrap(url, start_postgres=dialect_of(url) == "postgresql" and not args.no_docker)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
