# Database Setup Guide

**Status:** ✅ Completed (2025-11-19)

This guide documents the Neon PostgreSQL database setup for Copy That.

## Overview

Copy That uses **Neon** as its PostgreSQL database provider with:
- Async database operations (SQLAlchemy + asyncpg)
- Type-safe ORM with SQLAlchemy 2.0
- Database migrations via Alembic
- Connection pooling for production workloads

## Database Configuration

### Connection Details

**Project:** copy-that
**Provider:** Neon (icy-lake-85661769)
**Region:** AWS us-east-2
**PostgreSQL Version:** 17
**Database:** neondb

### Environment Variables

Connection string configured in `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]/neondb?ssl=require
```

## Database Schema

### Tables

#### `projects`
Stores design token extraction projects.

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | NULL |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT now() |

#### `extraction_jobs`
Tracks token extraction jobs from images/videos/audio.

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| project_id | INTEGER | NOT NULL |
| source_url | VARCHAR(512) | NOT NULL |
| extraction_type | VARCHAR(50) | NOT NULL |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'pending' |
| result_data | TEXT | NULL (JSON) |
| error_message | TEXT | NULL |
| created_at | TIMESTAMP | NOT NULL, DEFAULT now() |
| completed_at | TIMESTAMP | NULL |

**Extraction Types:** `color`, `spacing`, `typography`, `all`
**Status Values:** `pending`, `processing`, `completed`, `failed`

## Code Structure

### Database Layer

**Configuration:**
```
src/copy_that/infrastructure/database.py
```
- Async engine with connection pooling
- Session factory for dependency injection
- Base class for all models

**Models:**
```
src/copy_that/domain/models.py
```
- SQLAlchemy ORM models
- Type hints via `Mapped` and `mapped_column`

### Using the Database in FastAPI

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from copy_that.infrastructure.database import get_db
from copy_that.domain.models import Project

@app.get("/api/v1/projects")
async def get_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    return {"projects": [p.name for p in projects]}
```

## Database Migrations

### Alembic Configuration

Migrations are managed with Alembic:
```
alembic/
├── env.py              # Migration environment
├── versions/           # Migration files
└── alembic.ini         # Configuration
```

**Key Features:**
- Auto-detects schema changes from models
- Loads DATABASE_URL from `.env`
- Converts asyncpg URLs to psycopg2 for migrations
- Supports both online and offline migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column"

# Create empty migration
alembic revision -m "Custom migration"
```

### Applying Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade c1a36d61036a

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Migration History

| Version | Date | Description |
|---------|------|-------------|
| c1a36d61036a | 2025-11-19 | Initial schema: projects and extraction_jobs |

## Testing Database Connection

### Via API Endpoint

```bash
# Start the server
uvicorn copy_that.interfaces.api.main:app --reload

# Test database connection
curl http://localhost:8000/api/v1/db-test
```

Expected response:
```json
{
  "database": "connected",
  "provider": "Neon",
  "projects_count": 0,
  "message": "Database connection successful! 🎉"
}
```

### Via Python Shell

```python
import asyncio
from sqlalchemy import select
from copy_that.infrastructure.database import AsyncSessionLocal
from copy_that.domain.models import Project

async def test_db():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Project))
        projects = result.scalars().all()
        print(f"Found {len(projects)} projects")

asyncio.run(test_db())
```

### Via Neon MCP Server

```bash
# Using Claude Code's Neon integration
mcp__Neon__get_database_tables --projectId icy-lake-85661769
mcp__Neon__run_sql --projectId icy-lake-85661769 --sql "SELECT * FROM projects"
```

## Connection Pooling

Configured for production workloads:

```python
engine = create_async_engine(
    DATABASE_URL,
    echo=False,                    # Set True for SQL logging in dev
    pool_pre_ping=True,           # Verify connections before use
    pool_size=5,                  # Base pool size
    max_overflow=10,              # Additional connections under load
)
```

**Max Connections:** 15 (5 base + 10 overflow)
**Pre-ping:** Enabled (detects stale connections)

## Neon-Specific Features

### Autoscaling
Neon automatically scales compute based on load:
- Min: 0.25 CU (compute units)
- Max: 2 CU
- Auto-pause: After 5 minutes of inactivity

### Database Branching
Create database branches for development:

```bash
# Via MCP Server
mcp__Neon__create_branch --projectId icy-lake-85661769 --branchName "feature-x"

# Or via Neon CLI
neon branches create --project-id icy-lake-85661769 --name "feature-x"
```

### Point-in-Time Recovery
Restore database to any point in the last 7 days:

```bash
# Via Neon Console
https://console.neon.tech/app/projects/icy-lake-85661769
```

### Schema Migrations with Branching

For safe migrations:

1. Create a database branch
2. Apply migration to branch
3. Test on branch
4. Apply to main if successful

```bash
# Create branch
neon branches create --project-id icy-lake-85661769 --name "migration-test"

# Get branch connection string
BRANCH_URL=$(neon branches get --project-id icy-lake-85661769 --branch migration-test --output json | jq -r .connection_uri)

# Test migration on branch
DATABASE_URL=$BRANCH_URL alembic upgrade head

# If successful, apply to main
alembic upgrade head
```

## Dependencies

Installed packages for database operations:

```toml
dependencies = [
    "sqlalchemy>=2.0.25",      # Async ORM
    "alembic>=1.13.0",         # Migrations
    "asyncpg>=0.29.0",         # Async PostgreSQL driver
    "psycopg2-binary>=2.9.0",  # Sync driver for Alembic
    "python-dotenv>=1.0.0",    # Load .env files
]
```

## Security

- ✅ SSL/TLS encryption enabled (`?ssl=require`)
- ✅ Connection string stored in `.env` (gitignored)
- ✅ Password not logged in application
- ✅ Connection pooling prevents exhaustion
- ✅ Pre-ping prevents stale connections
- ✅ Neon SOC 2 Type II certified

## Troubleshooting

### Connection Timeout

Check network connectivity:
```bash
psql "postgresql://[user]:[password]@[host]/neondb?ssl=require"
```

### Migration Conflicts

Reset to clean state:
```bash
# Stamp current version
alembic stamp head

# Or downgrade and re-apply
alembic downgrade base
alembic upgrade head
```

### Async/Sync Driver Mismatch

- **Application:** Use `postgresql+asyncpg://` (async)
- **Alembic:** Uses `postgresql+psycopg2://` (sync, auto-converted)

### Pool Exhausted

Increase pool size in `database.py`:
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # Increase from 5
    max_overflow=20,        # Increase from 10
)
```

## Monitoring

### Connection Stats

Query active connections:
```sql
SELECT
    count(*) as total_connections,
    state,
    application_name
FROM pg_stat_activity
WHERE datname = 'neondb'
GROUP BY state, application_name;
```

### Database Size

```sql
SELECT pg_size_pretty(pg_database_size('neondb')) as size;
```

### Table Sizes

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Future Enhancements

### Planned Features

- [ ] Multi-tenancy via row-level security (RLS)
- [ ] Read replicas for analytics queries
- [ ] Full-text search with `pg_trgm`
- [ ] JSON aggregation for token exports
- [ ] Database seeding for development
- [ ] Backup automation via Neon snapshots

### Schema Evolution

Future tables planned:
- `color_tokens` - Extracted color palettes
- `spacing_tokens` - Spacing/layout measurements
- `typography_tokens` - Font and text styles
- `users` - User accounts (when auth is added)
- `organizations` - Multi-tenancy support

## Resources

- **Neon Docs:** https://neon.tech/docs
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/en/20/
- **Alembic Docs:** https://alembic.sqlalchemy.org/
- **asyncpg Docs:** https://magicstack.github.io/asyncpg/

---

**Setup Date:** 2025-11-19
**Database Version:** PostgreSQL 17
**Last Updated:** 2025-11-19
