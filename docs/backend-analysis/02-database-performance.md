# Database & Performance Analysis

**Focus Area: 35% of Evaluation Effort**

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [Optimization Strategy](#2-optimization-strategy)
3. [Performance Benchmarking Plan](#3-performance-benchmarking-plan)
4. [Recommendations](#4-recommendations)

---

## 1. Current State Assessment

### 1.1 Database Architecture

**Technology Stack**:
- PostgreSQL 17 (Neon serverless)
- SQLAlchemy 2.0 with async support
- Alembic for migrations
- Redis for caching/queuing

**Connection Configuration**:
```python
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("ENVIRONMENT") == "local",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
```

### 1.2 Data Model Analysis

#### 7 Core Models

```
Project
  ├─> ExtractionJob (1:N)
  ├─> ColorToken (1:N)
  └─> ExtractionSession (1:N)
      └─> TokenLibrary (1:N)
          ├─> TokenExport (1:N)
          └─> ColorToken (1:N)
```

#### ColorToken Model (50+ fields)

**Core Properties** (7 fields):
- id, project_id, extraction_job_id, hex, rgb, name, confidence

**Design System** (3 fields):
- design_intent, semantic_names (JSON), category, role

**Color Analysis** (7 fields):
- harmony, temperature, saturation_level, lightness_level, hsl, hsv

**Accessibility** (7 fields):
- wcag_contrast_on_white/black, wcag_aa/aaa_compliant_text/normal, colorblind_safe

**ML/CV Properties** (4 fields):
- kmeans_cluster_id, sam_segmentation_mask, clip_embeddings (JSON), histogram_significance

**Metadata** (3 fields):
- extraction_metadata (JSON), provenance (JSON), library_id

### 1.3 Query Pattern Audit

#### Pattern 1: Simple SELECT (Good)
```python
# colors.py:77-78
result = await db.execute(select(Project).where(Project.id == request.project_id))
project = result.scalar_one_or_none()
```
**Assessment**: Single query, efficient

#### Pattern 2: N+1 in Role Assignment (Bad)
```python
# sessions.py:195-207
for assignment in request.role_assignments:  # N items
    token_result = await db.execute(
        select(ColorToken).where(ColorToken.id == assignment.token_id)
    )
    token = token_result.scalar_one_or_none()
    if token and token.library_id == library.id:
        token.role = assignment.role
```
**Issue**: One SELECT per assignment (50 assignments = 50 queries)

#### Pattern 3: Unnecessary Refetch (Bad)
```python
# colors.py:284-291
# After inserting colors...
result = await db.execute(
    select(ColorToken)
    .where(ColorToken.project_id == request.project_id)
    .order_by(ColorToken.created_at.desc())
    .limit(len(extraction_result.colors))
)
stored_colors = result.scalars().all()
```
**Issue**: Refetches ALL project colors after insert

#### Pattern 4: Multi-step Navigation (Medium)
```python
# sessions.py:101-141
# Step 1: Get session
session_result = await db.execute(select(ExtractionSession).where(...))

# Step 2: Get library
lib_result = await db.execute(select(TokenLibrary).where(...))

# Step 3: Get tokens (if library exists)
if library:
    tokens_result = await db.execute(select(ColorToken).where(...))
```
**Issue**: 3 sequential queries, could use joins

### 1.4 Index Coverage Analysis

#### Current Indexes (6 defined in migration 006)

```sql
ix_extraction_sessions_project_id  → extraction_sessions(project_id)
ix_token_libraries_session_id      → token_libraries(session_id)
ix_token_libraries_token_type      → token_libraries(token_type)
ix_token_exports_library_id        → token_exports(library_id)
ix_color_tokens_library_id         → color_tokens(library_id)
ix_color_tokens_role               → color_tokens(role)
```

#### Missing Critical Indexes

| Table | Column(s) | Query Pattern | Impact |
|-------|-----------|---------------|--------|
| color_tokens | project_id | WHERE project_id = ? | High |
| color_tokens | project_id, created_at | ORDER BY created_at | High |
| extraction_jobs | project_id | WHERE project_id = ? | Medium |
| extraction_jobs | status | WHERE status = ? | Medium |
| color_tokens | extraction_job_id | JOIN operations | Medium |

### 1.5 Migration Quality Review

**6 Migrations Analyzed**:

| Migration | Purpose | Quality |
|-----------|---------|---------|
| c1a36d61036a | Initial schema | Missing FK constraints |
| 2025_11_19_001 | Color tokens | Missing indexes |
| 2025_11_19_002 | Expand tokens | Good downgrade |
| 2025_11_20_003 | Semantic names | Simple |
| 2025_11_20_004 | Rename column | Simple |
| 2025_11_20_006 | Session/Library | Best quality |

**Issues Found**:
- No foreign key constraints in early migrations
- No CASCADE delete policies
- No check constraints for enum fields
- Auto-generated constraint names (not predictable)

### 1.6 Connection Pooling Evaluation

**Current Configuration**:
```python
pool_size = 5
max_overflow = 10
# Total capacity: 15 connections
```

**Capacity Analysis**:
- Uvicorn workers: 4-8 typical
- Requests per worker: 10-20 concurrent
- Total potential: 40-160 concurrent requests
- **Bottleneck**: 15 connections << 160 requests

**Missing Configuration**:
- `pool_recycle` - Connection refresh
- `pool_timeout` - Wait timeout
- Connection health monitoring

### 1.7 Redis Caching Strategy

**Current Implementation**: Limited to Celery task queue

**Configuration** (per environment):
```python
configs = {
    "local": {
        "REDIS_URL": "redis://localhost:6379/0",
        "CELERY_BROKER_URL": "redis://localhost:6379/1",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/2",
    },
    "staging": {
        "REDIS_URL": "redis://...@upstash.io:6379",
        # ...
    }
}
```

**Missing Features**:
- No application-level caching
- No cache invalidation strategy
- No TTL configuration
- No cache key versioning

---

## 2. Optimization Strategy

### 2.1 Database Indexing Recommendations

#### Priority 1: Critical Indexes

```sql
-- Most impactful: project_id lookups
CREATE INDEX ix_color_tokens_project_id
ON color_tokens(project_id);

-- Second most impactful: sorted listings
CREATE INDEX ix_color_tokens_project_created
ON color_tokens(project_id, created_at DESC);

-- Job lookups
CREATE INDEX ix_extraction_jobs_project_id
ON extraction_jobs(project_id);
```

#### Priority 2: Filtering Indexes

```sql
-- Status filtering
CREATE INDEX ix_extraction_jobs_status
ON extraction_jobs(status);

-- Type filtering
CREATE INDEX ix_extraction_jobs_type
ON extraction_jobs(extraction_type);

-- Design intent queries
CREATE INDEX ix_color_tokens_design_intent
ON color_tokens(design_intent);
```

#### Priority 3: Composite Indexes

```sql
-- Common query pattern
CREATE INDEX ix_color_tokens_library_project
ON color_tokens(library_id, project_id);

-- Job status per project
CREATE INDEX ix_extraction_jobs_project_status
ON extraction_jobs(project_id, status);
```

#### Migration File

```python
# alembic/versions/2025_11_22_add_indexes.py
"""Add performance indexes

Revision ID: add_indexes_001
"""

def upgrade():
    # Priority 1
    op.create_index(
        'ix_color_tokens_project_id',
        'color_tokens',
        ['project_id']
    )
    op.create_index(
        'ix_color_tokens_project_created',
        'color_tokens',
        ['project_id', sa.text('created_at DESC')]
    )
    op.create_index(
        'ix_extraction_jobs_project_id',
        'extraction_jobs',
        ['project_id']
    )

    # Priority 2
    op.create_index(
        'ix_extraction_jobs_status',
        'extraction_jobs',
        ['status']
    )
    op.create_index(
        'ix_color_tokens_design_intent',
        'color_tokens',
        ['design_intent']
    )

def downgrade():
    op.drop_index('ix_color_tokens_project_id')
    op.drop_index('ix_color_tokens_project_created')
    op.drop_index('ix_extraction_jobs_project_id')
    op.drop_index('ix_extraction_jobs_status')
    op.drop_index('ix_color_tokens_design_intent')
```

### 2.2 Eager Loading Patterns

#### Add ORM Relationships

```python
# domain/models.py

class Project(Base):
    __tablename__ = "projects"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(255), nullable=False)
    # ...

    # Add relationships
    extraction_jobs: Mapped[list["ExtractionJob"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )
    color_tokens: Mapped[list["ColorToken"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )
    sessions: Mapped[list["ExtractionSession"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )


class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"

    # ...
    project_id = mapped_column(ForeignKey("projects.id"), nullable=False)

    # Add relationship
    project: Mapped["Project"] = relationship(back_populates="extraction_jobs")
    color_tokens: Mapped[list["ColorToken"]] = relationship(
        back_populates="extraction_job"
    )


class TokenLibrary(Base):
    __tablename__ = "token_libraries"

    # ...
    session_id = mapped_column(ForeignKey("extraction_sessions.id"), nullable=False)

    # Add relationships
    session: Mapped["ExtractionSession"] = relationship(back_populates="libraries")
    color_tokens: Mapped[list["ColorToken"]] = relationship(
        back_populates="library",
        cascade="all, delete-orphan"
    )
    exports: Mapped[list["TokenExport"]] = relationship(
        back_populates="library",
        cascade="all, delete-orphan"
    )
```

#### Eager Loading Queries

```python
# Before: 3 queries
session = await db.execute(select(ExtractionSession).where(...))
library = await db.execute(select(TokenLibrary).where(...))
tokens = await db.execute(select(ColorToken).where(...))

# After: 1 query with eager loading
from sqlalchemy.orm import selectinload, joinedload

result = await db.execute(
    select(ExtractionSession)
    .where(ExtractionSession.id == session_id)
    .options(
        selectinload(ExtractionSession.libraries)
        .selectinload(TokenLibrary.color_tokens)
    )
)
session = result.scalar_one_or_none()
# Access session.libraries[0].color_tokens directly
```

### 2.3 Redis Caching Layer Design

```python
# infrastructure/cache/redis_cache.py

import json
import hashlib
from typing import Any, Optional
from redis.asyncio import Redis
from datetime import timedelta

class RedisCache:
    """Application-level Redis caching"""

    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = timedelta(hours=1)
        self.prefix = "copythat:"

    def _make_key(self, namespace: str, identifier: str) -> str:
        """Generate cache key with prefix and namespace"""
        return f"{self.prefix}{namespace}:{identifier}"

    async def get(self, namespace: str, identifier: str) -> Optional[Any]:
        """Get cached value"""
        key = self._make_key(namespace, identifier)
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        namespace: str,
        identifier: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ):
        """Set cached value with TTL"""
        key = self._make_key(namespace, identifier)
        ttl = ttl or self.default_ttl
        await self.redis.setex(
            key,
            int(ttl.total_seconds()),
            json.dumps(value, default=str)
        )

    async def delete(self, namespace: str, identifier: str):
        """Delete cached value"""
        key = self._make_key(namespace, identifier)
        await self.redis.delete(key)

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        full_pattern = f"{self.prefix}{pattern}"
        keys = await self.redis.keys(full_pattern)
        if keys:
            await self.redis.delete(*keys)


class CachedColorService:
    """Color service with caching layer"""

    def __init__(self, db: AsyncSession, cache: RedisCache):
        self.db = db
        self.cache = cache

    async def get_project_colors(self, project_id: int) -> list[dict]:
        """Get colors with caching"""

        # Check cache first
        cached = await self.cache.get("project_colors", str(project_id))
        if cached:
            return cached

        # Query database
        result = await self.db.execute(
            select(ColorToken)
            .where(ColorToken.project_id == project_id)
            .order_by(ColorToken.created_at.desc())
        )
        colors = result.scalars().all()

        # Serialize for cache
        color_dicts = [
            {
                "id": c.id,
                "hex": c.hex,
                "name": c.name,
                "confidence": c.confidence,
                # ... other fields
            }
            for c in colors
        ]

        # Cache result (1 hour TTL)
        await self.cache.set(
            "project_colors",
            str(project_id),
            color_dicts,
            timedelta(hours=1)
        )

        return color_dicts

    async def invalidate_project_cache(self, project_id: int):
        """Invalidate cache when colors change"""
        await self.cache.delete("project_colors", str(project_id))
```

### 2.4 Connection Pool Tuning for Neon

```python
# infrastructure/database.py

def create_engine_with_optimized_pool(database_url: str):
    """Create engine with Neon-optimized pooling"""

    # Parse URL and add SSL
    if "localhost" not in database_url:
        # Neon requires SSL
        ssl_args = {"ssl": True}
    else:
        ssl_args = {}

    # Optimized pool settings for serverless
    pool_settings = {
        # Increased pool for higher concurrency
        "pool_size": 20,
        "max_overflow": 20,

        # Connection lifecycle
        "pool_recycle": 1800,  # Recycle after 30 minutes
        "pool_pre_ping": True,  # Verify connection health
        "pool_timeout": 30,     # Wait 30s for connection

        # Neon-specific: connections can go stale
        "pool_reset_on_return": "rollback",
    }

    engine = create_async_engine(
        database_url,
        echo=os.getenv("ENVIRONMENT") == "local",
        connect_args=ssl_args,
        **pool_settings
    )

    return engine


# For Neon serverless, consider connection pooler
def get_neon_pooler_url(base_url: str) -> str:
    """
    Convert direct Neon URL to pooler URL

    Neon provides PgBouncer-like pooling at:
    ep-name-123456-pooler.us-east-2.aws.neon.tech

    This allows more concurrent connections
    """
    # Example transformation
    # From: postgresql+asyncpg://user:pass@ep-name-123456.us-east-2.aws.neon.tech/db
    # To:   postgresql+asyncpg://user:pass@ep-name-123456-pooler.us-east-2.aws.neon.tech/db

    return base_url.replace(".us-east-2.aws", "-pooler.us-east-2.aws")
```

### 2.5 Query Optimization Examples

#### Before/After: N+1 Fix

**Before** (sessions.py:195-207):
```python
# 50 role assignments = 50 SELECT queries
for assignment in request.role_assignments:
    token_result = await db.execute(
        select(ColorToken).where(ColorToken.id == assignment.token_id)
    )
    token = token_result.scalar_one_or_none()
    if token and token.library_id == library.id:
        token.role = assignment.role
```

**After**:
```python
# 1 SELECT + 1 UPDATE
token_ids = [a.token_id for a in request.role_assignments]
role_map = {a.token_id: a.role for a in request.role_assignments}

# Batch fetch all tokens
result = await db.execute(
    select(ColorToken)
    .where(ColorToken.id.in_(token_ids))
    .where(ColorToken.library_id == library.id)
)
tokens = result.scalars().all()

# Batch update
for token in tokens:
    token.role = role_map[token.id]

await db.commit()
```

**Impact**: 50 queries → 1 query

#### Before/After: Unnecessary Refetch

**Before** (colors.py:284-291):
```python
# Insert colors, then refetch ALL project colors
for color_data in extraction_result.colors:
    color_token = ColorToken(**color_data)
    db.add(color_token)

await db.flush()

# Unnecessary: fetches all project colors just to return inserted ones
result = await db.execute(
    select(ColorToken)
    .where(ColorToken.project_id == request.project_id)
    .order_by(ColorToken.created_at.desc())
    .limit(len(extraction_result.colors))
)
stored_colors = result.scalars().all()
```

**After**:
```python
# Insert and return directly
inserted_colors = []
for color_data in extraction_result.colors:
    color_token = ColorToken(**color_data)
    db.add(color_token)
    inserted_colors.append(color_token)

await db.flush()

# Refresh to get generated IDs
for color in inserted_colors:
    await db.refresh(color)

# Return inserted colors directly
return inserted_colors
```

**Impact**: Eliminates extra SELECT, prevents race conditions

#### Before/After: Multi-Step Navigation

**Before**:
```python
# 3 sequential queries
session = (await db.execute(
    select(ExtractionSession).where(ExtractionSession.id == session_id)
)).scalar_one_or_none()

library = (await db.execute(
    select(TokenLibrary)
    .where(TokenLibrary.session_id == session_id)
    .where(TokenLibrary.token_type == "color")
)).scalar_one_or_none()

if library:
    tokens = (await db.execute(
        select(ColorToken).where(ColorToken.library_id == library.id)
    )).scalars().all()
```

**After** (with relationships):
```python
# 1 query with eager loading
result = await db.execute(
    select(ExtractionSession)
    .where(ExtractionSession.id == session_id)
    .options(
        selectinload(ExtractionSession.libraries)
        .selectinload(TokenLibrary.color_tokens)
    )
)
session = result.scalar_one_or_none()

# Access via relationships
library = next(
    (lib for lib in session.libraries if lib.token_type == "color"),
    None
)
tokens = library.color_tokens if library else []
```

**Impact**: 3 queries → 1 query

---

## 3. Performance Benchmarking Plan

### 3.1 Key Metrics to Track

| Metric | Description | Target | Tool |
|--------|-------------|--------|------|
| Query time (p50) | Median query execution | <50ms | DB logs |
| Query time (p99) | 99th percentile | <200ms | DB logs |
| Connection wait | Pool acquisition time | <10ms | SQLAlchemy events |
| N+1 queries | Queries per request | <5 | Query counter |
| Cache hit rate | Redis cache effectiveness | >40% | Redis metrics |
| Memory usage | ORM object overhead | <100MB/worker | Process metrics |

### 3.2 Performance Testing Strategy

#### Load Test Configuration

```python
# tests/performance/test_load.py

from locust import HttpUser, task, between

class ColorAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_project_colors(self):
        """Most common operation"""
        self.client.get(f"/api/v1/projects/{self.project_id}/colors")

    @task(1)
    def extract_colors(self):
        """Resource-intensive operation"""
        self.client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": self.project_id,
                "image_url": "https://example.com/test.jpg",
                "max_colors": 10
            }
        )

    @task(2)
    def get_session_library(self):
        """Multi-table query"""
        self.client.get(f"/api/v1/sessions/{self.session_id}/library")
```

#### Benchmark Scenarios

| Scenario | Concurrent Users | Duration | Success Criteria |
|----------|------------------|----------|------------------|
| Baseline | 10 | 5 min | Establish metrics |
| Normal load | 50 | 10 min | p99 < 500ms |
| Peak load | 100 | 10 min | p99 < 1s, 0 errors |
| Stress test | 200 | 5 min | Graceful degradation |
| Soak test | 50 | 1 hour | No memory leaks |

### 3.3 Optimization Targets

| Component | Current (est.) | Target | Method |
|-----------|----------------|--------|--------|
| Project colors query | 100ms | 20ms | Add index |
| Role assignment | 500ms (50 queries) | 50ms (1 query) | Batch fetch |
| Session library load | 150ms (3 queries) | 50ms (1 query) | Eager loading |
| Connection acquisition | Unknown | <10ms | Increase pool |
| Cache hit rate | 0% | 40% | Implement caching |

### 3.4 Monitoring Dashboard Design

```python
# Prometheus metrics for database monitoring

from prometheus_client import Counter, Histogram, Gauge

# Query metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type', 'table']
)

db_query_count = Counter(
    'db_queries_total',
    'Total database queries',
    ['query_type', 'table']
)

# Pool metrics
db_pool_size = Gauge(
    'db_pool_connections',
    'Database pool connections',
    ['state']  # active, idle, overflow
)

db_pool_wait = Histogram(
    'db_pool_wait_seconds',
    'Time waiting for pool connection'
)

# Cache metrics
cache_operations = Counter(
    'cache_operations_total',
    'Cache operations',
    ['operation', 'result']  # get/set, hit/miss
)
```

---

## 4. Recommendations

### 4.1 Immediate Actions (This Week)

| Priority | Action | Effort | Impact | File |
|----------|--------|--------|--------|------|
| 1 | Add missing indexes | 1 hour | High | New migration |
| 2 | Fix N+1 in role assignment | 1 hour | High | sessions.py |
| 3 | Remove unnecessary refetch | 30 min | Medium | colors.py |
| 4 | Increase pool size to 20 | 15 min | Medium | database.py |

### 4.2 Short-term (Next 2 Weeks)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Add ORM relationships | 4 hours | High |
| 2 | Implement Redis caching | 8 hours | High |
| 3 | Add pool timeout config | 1 hour | Medium |
| 4 | Add cascade deletes | 2 hours | Medium |

### 4.3 Medium-term (Next Month)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Add performance monitoring | 8 hours | High |
| 2 | Implement eager loading patterns | 4 hours | Medium |
| 3 | Add transaction isolation | 4 hours | Medium |
| 4 | Optimize JSON field handling | 4 hours | Low |

### 4.4 Architecture Improvements

#### Add Foreign Key Constraints

```python
# Migration to add missing FK constraints
def upgrade():
    # ColorToken → Project
    op.create_foreign_key(
        'fk_color_tokens_project_id',
        'color_tokens',
        'projects',
        ['project_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # ExtractionJob → Project
    op.create_foreign_key(
        'fk_extraction_jobs_project_id',
        'extraction_jobs',
        'projects',
        ['project_id'],
        ['id'],
        ondelete='CASCADE'
    )
```

#### Add Check Constraints

```python
# Migration for enum validation
def upgrade():
    op.create_check_constraint(
        'ck_extraction_jobs_status',
        'extraction_jobs',
        "status IN ('pending', 'processing', 'completed', 'failed')"
    )

    op.create_check_constraint(
        'ck_color_tokens_role',
        'color_tokens',
        "role IN ('primary', 'secondary', 'accent', 'success', 'error', 'warning', 'info', 'background', 'surface', 'text')"
    )
```

### 4.5 Summary Score Improvements

| Aspect | Current | After Phase 1 | After Phase 2 |
|--------|---------|---------------|---------------|
| Query patterns | 5/10 | 7/10 | 9/10 |
| Indexing | 4/10 | 8/10 | 9/10 |
| Connection management | 6/10 | 7/10 | 8/10 |
| Caching | 5/10 | 5/10 | 8/10 |
| **Overall** | **6.5/10** | **7.5/10** | **8.5/10** |

---

## File Reference

| File | Issues Found | Priority |
|------|--------------|----------|
| `sessions.py:195-207` | N+1 query | Critical |
| `colors.py:284-291` | Unnecessary refetch | High |
| `database.py:57-58` | Low pool size | Medium |
| `models.py` | Missing relationships | Medium |
| `alembic/versions/` | Missing indexes | High |

---

*Next: [03-security-hardening.md](./03-security-hardening.md)*
