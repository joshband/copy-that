# Implementation Roadmap

**Phased Implementation Plan with Testing Strategy**

---

## Table of Contents

1. [Implementation Phases](#1-implementation-phases)
2. [Testing Strategy](#2-testing-strategy)
3. [Monitoring & Observability](#3-monitoring--observability)
4. [Migration Scripts](#4-migration-scripts)

---

## 1. Implementation Phases

### Phase 1: Critical Security Fixes + Quick Wins (Week 1)

**Effort**: 20-24 hours
**Risk**: Low (foundational changes)
**Priority**: Production Blockers

#### Day 1-2: Authentication System

```python
# Task 1.1: Create User and APIKey models
# File: src/copy_that/domain/models.py

# Add to existing models.py - see 03-security-hardening.md for full implementation

# Task 1.2: Create auth migration
# Run: alembic revision -m "add_user_authentication"
```

**Migration**:
```python
# alembic/versions/2025_11_22_auth.py

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('roles', sa.JSON(), default=['user']),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('last_login', sa.DateTime()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('key_prefix', sa.String(8), nullable=False),
        sa.Column('scopes', sa.JSON(), default=['read']),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('last_used_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])

    # Add owner_id to projects
    op.add_column('projects', sa.Column('owner_id', sa.String(36)))
    op.create_foreign_key(
        'fk_projects_owner_id',
        'projects', 'users',
        ['owner_id'], ['id']
    )

def downgrade():
    op.drop_constraint('fk_projects_owner_id', 'projects')
    op.drop_column('projects', 'owner_id')
    op.drop_table('api_keys')
    op.drop_table('users')
```

#### Day 2-3: Remove Hardcoded Secrets

```python
# Task 1.3: Implement GCP Secret Manager
# File: src/copy_that/infrastructure/security/secrets_manager.py
# See 03-security-hardening.md for full implementation

# Task 1.4: Update config.py to use secrets
# File: src/copy_that/infrastructure/config.py

from .security.secrets_manager import get_secret

def get_config():
    """Get configuration with secrets from Secret Manager"""
    environment = os.getenv("ENVIRONMENT", "local")

    if environment in ("staging", "production"):
        return {
            "DATABASE_URL": get_secret("database-url"),
            "REDIS_URL": get_secret("redis-url"),
            "SECRET_KEY": get_secret("jwt-secret-key"),
            "ANTHROPIC_API_KEY": get_secret("anthropic-api-key"),
            "OPENAI_API_KEY": get_secret("openai-api-key"),
        }
    else:
        # Local development uses environment variables
        return {
            "DATABASE_URL": os.getenv("DATABASE_URL"),
            "REDIS_URL": os.getenv("REDIS_URL"),
            "SECRET_KEY": os.getenv("SECRET_KEY"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        }
```

#### Day 3-4: Database Quick Wins

```python
# Task 1.5: Add missing indexes
# Run: alembic revision -m "add_performance_indexes"

def upgrade():
    # Critical indexes
    op.create_index('ix_color_tokens_project_id', 'color_tokens', ['project_id'])
    op.create_index(
        'ix_color_tokens_project_created',
        'color_tokens',
        ['project_id', sa.text('created_at DESC')]
    )
    op.create_index('ix_extraction_jobs_project_id', 'extraction_jobs', ['project_id'])

    # Filtering indexes
    op.create_index('ix_extraction_jobs_status', 'extraction_jobs', ['status'])
    op.create_index('ix_color_tokens_design_intent', 'color_tokens', ['design_intent'])

def downgrade():
    op.drop_index('ix_color_tokens_project_id')
    op.drop_index('ix_color_tokens_project_created')
    op.drop_index('ix_extraction_jobs_project_id')
    op.drop_index('ix_extraction_jobs_status')
    op.drop_index('ix_color_tokens_design_intent')
```

```python
# Task 1.6: Fix N+1 query in role assignment
# File: src/copy_that/interfaces/api/sessions.py

# Replace lines 195-207
async def assign_roles(
    session_id: int,
    request: AssignRolesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify ownership
    session = await get_owned_session(session_id, db, current_user)

    # Get library
    library = await db.execute(
        select(TokenLibrary)
        .where(TokenLibrary.session_id == session_id)
        .where(TokenLibrary.token_type == "color")
    )
    library = library.scalar_one_or_none()

    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    # FIXED: Batch fetch all tokens
    token_ids = [a.token_id for a in request.role_assignments]
    role_map = {a.token_id: a.role for a in request.role_assignments}

    result = await db.execute(
        select(ColorToken)
        .where(ColorToken.id.in_(token_ids))
        .where(ColorToken.library_id == library.id)
    )
    tokens = result.scalars().all()

    # Batch update
    updated_count = 0
    for token in tokens:
        if token.id in role_map:
            token.role = role_map[token.id]
            updated_count += 1

    await db.commit()

    return {"updated": updated_count, "total": len(request.role_assignments)}
```

#### Day 4-5: Connection Pool & Basic Rate Limiting

```python
# Task 1.7: Update connection pool settings
# File: src/copy_that/infrastructure/database.py

# Update engine creation
if "sqlite" not in DATABASE_URL:
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 20,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
        "pool_timeout": 30,
    })
```

```python
# Task 1.8: Add basic rate limiting
# File: src/copy_that/interfaces/api/main.py

from ..security.rate_limiter import RateLimitMiddleware
from ...infrastructure.cache.redis_cache import get_redis

# In create_application():
redis = await get_redis()
app.add_middleware(
    RateLimitMiddleware,
    redis=redis,
    requests_per_minute=60,
    requests_per_hour=1000
)
```

### Phase 1 Deliverables Checklist

- [ ] User authentication with JWT
- [ ] Auth router (register, login, refresh, me)
- [ ] Project ownership (owner_id foreign key)
- [ ] GCP Secret Manager integration
- [ ] Remove all hardcoded credentials
- [ ] Add 5 critical database indexes
- [ ] Fix N+1 in role assignment
- [ ] Increase connection pool to 20
- [ ] Basic rate limiting (60/min, 1000/hr)

---

### Phase 2: Database Optimization + AI Cost Reduction (Week 2-3)

**Effort**: 30-40 hours
**Risk**: Medium (performance changes)

#### ORM Relationships & Eager Loading

```python
# Task 2.1: Add ORM relationships
# File: src/copy_that/domain/models.py

class Project(Base):
    __tablename__ = "projects"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(255), nullable=False)
    description = mapped_column(Text)
    owner_id = mapped_column(ForeignKey("users.id"))
    created_at = mapped_column(DateTime, default=utc_now)
    updated_at = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="projects")
    extraction_jobs: Mapped[list["ExtractionJob"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    color_tokens: Mapped[list["ColorToken"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    sessions: Mapped[list["ExtractionSession"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )


class TokenLibrary(Base):
    __tablename__ = "token_libraries"

    # ... existing columns ...

    # Relationships
    session: Mapped["ExtractionSession"] = relationship(back_populates="libraries")
    color_tokens: Mapped[list["ColorToken"]] = relationship(
        back_populates="library",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    exports: Mapped[list["TokenExport"]] = relationship(
        back_populates="library",
        cascade="all, delete-orphan"
    )
```

```python
# Task 2.2: Update queries to use eager loading
# File: src/copy_that/interfaces/api/sessions.py

from sqlalchemy.orm import selectinload

async def get_session_with_library(session_id: int, db: AsyncSession):
    """Get session with library and tokens in one query"""
    result = await db.execute(
        select(ExtractionSession)
        .where(ExtractionSession.id == session_id)
        .options(
            selectinload(ExtractionSession.libraries)
            .selectinload(TokenLibrary.color_tokens)
        )
    )
    return result.scalar_one_or_none()
```

#### Redis Caching Layer

```python
# Task 2.3: Implement Redis caching service
# File: src/copy_that/infrastructure/cache/color_cache.py

from redis.asyncio import Redis
import json
from datetime import timedelta

class ColorCacheService:
    """Caching service for color operations"""

    def __init__(self, redis: Redis):
        self.redis = redis
        self.prefix = "copythat:colors:"

    async def get_project_colors(self, project_id: int) -> list[dict] | None:
        """Get cached project colors"""
        key = f"{self.prefix}project:{project_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set_project_colors(
        self,
        project_id: int,
        colors: list[dict],
        ttl: timedelta = timedelta(hours=1)
    ):
        """Cache project colors"""
        key = f"{self.prefix}project:{project_id}"
        await self.redis.setex(key, int(ttl.total_seconds()), json.dumps(colors))

    async def invalidate_project(self, project_id: int):
        """Invalidate cache when colors change"""
        key = f"{self.prefix}project:{project_id}"
        await self.redis.delete(key)

    async def get_extraction_result(self, image_hash: str) -> dict | None:
        """Get cached AI extraction result"""
        key = f"{self.prefix}extraction:{image_hash}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set_extraction_result(
        self,
        image_hash: str,
        result: dict,
        ttl: timedelta = timedelta(hours=24)
    ):
        """Cache AI extraction result"""
        key = f"{self.prefix}extraction:{image_hash}"
        await self.redis.setex(key, int(ttl.total_seconds()), json.dumps(result))
```

#### AI Cost Tracking

```python
# Task 2.4: Create API usage logging model
# File: src/copy_that/domain/models.py

class APIUsageLog(Base):
    """Track AI API usage for cost monitoring"""
    __tablename__ = "api_usage_logs"

    id = mapped_column(Integer, primary_key=True)
    timestamp = mapped_column(DateTime, default=utc_now, index=True)
    user_id = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    project_id = mapped_column(Integer, ForeignKey("projects.id"), nullable=True)

    # Request details
    model = mapped_column(String(100), nullable=False)
    endpoint = mapped_column(String(255))

    # Token usage
    input_tokens = mapped_column(Integer, nullable=False)
    output_tokens = mapped_column(Integer, nullable=False)

    # Cost
    cost_usd = mapped_column(Float, nullable=False)

    # Metadata
    cached = mapped_column(Boolean, default=False)
    success = mapped_column(Boolean, default=True)
    error_type = mapped_column(String(100))

    # Indexes
    __table_args__ = (
        Index('ix_api_usage_user_date', 'user_id', 'timestamp'),
        Index('ix_api_usage_model', 'model'),
    )
```

```python
# Task 2.5: Implement cost tracking service
# File: src/copy_that/application/cost_tracker.py

class CostTracker:
    """Track and report API costs"""

    MODEL_COSTS = {
        "claude-sonnet-4-5-20250929": {"input": 0.003, "output": 0.015},
        "gpt-4o": {"input": 0.01, "output": 0.03},
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        user_id: str = None,
        project_id: int = None,
        cached: bool = False
    ):
        """Log API usage"""
        costs = self.MODEL_COSTS.get(model, {"input": 0.01, "output": 0.03})
        cost_usd = (
            (input_tokens / 1000 * costs["input"]) +
            (output_tokens / 1000 * costs["output"])
        )

        log = APIUsageLog(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            user_id=user_id,
            project_id=project_id,
            cached=cached
        )

        self.db.add(log)
        await self.db.commit()

        return cost_usd

    async def get_daily_cost(self, user_id: str = None) -> float:
        """Get today's total cost"""
        today = datetime.utcnow().date()

        query = select(func.sum(APIUsageLog.cost_usd)).where(
            func.date(APIUsageLog.timestamp) == today
        )

        if user_id:
            query = query.where(APIUsageLog.user_id == user_id)

        result = await self.db.execute(query)
        return result.scalar() or 0.0

    async def get_cost_report(self, days: int = 30) -> dict:
        """Generate cost report"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Total cost
        total = await self.db.execute(
            select(func.sum(APIUsageLog.cost_usd))
            .where(APIUsageLog.timestamp >= cutoff)
        )

        # By model
        by_model = await self.db.execute(
            select(
                APIUsageLog.model,
                func.sum(APIUsageLog.cost_usd),
                func.count(APIUsageLog.id)
            )
            .where(APIUsageLog.timestamp >= cutoff)
            .group_by(APIUsageLog.model)
        )

        # Cache savings
        cache_savings = await self.db.execute(
            select(func.sum(APIUsageLog.cost_usd))
            .where(APIUsageLog.timestamp >= cutoff)
            .where(APIUsageLog.cached == True)
        )

        return {
            "total_cost": total.scalar() or 0,
            "by_model": [
                {"model": m, "cost": c, "requests": r}
                for m, c, r in by_model.all()
            ],
            "cache_savings": cache_savings.scalar() or 0,
            "period_days": days
        }
```

#### Claude JSON Mode

```python
# Task 2.6: Update Claude extractor to use JSON mode
# File: src/copy_that/application/color_extractor.py

class AIColorExtractor:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-5-20250929"

    async def extract(self, image_data: bytes, max_colors: int = 10):
        # Updated prompt requesting JSON
        prompt = f"""Analyze this image and extract a color palette.

Return ONLY valid JSON in this exact format:
{{
  "colors": [
    {{
      "hex": "#XXXXXX",
      "name": "Color Name",
      "design_intent": "primary|secondary|accent|...",
      "confidence": 0.0-1.0,
      "usage": ["array", "of", "uses"],
      "prominence_percentage": 0-100
    }}
  ],
  "dominant_colors": ["#XXXXXX", "#XXXXXX", "#XXXXXX"],
  "palette_description": "One sentence description",
  "overall_confidence": 0.0-1.0
}}

Extract exactly {max_colors} colors. Return ONLY the JSON object."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64.b64encode(image_data).decode()
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        )

        # Parse JSON response
        response_text = message.content[0].text

        # Track usage
        await self.cost_tracker.log_usage(
            model=self.model,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens
        )

        try:
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
                return AIExtractionOutput(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Failed to parse Claude response: {e}")
            # Fall back to regex parsing
            return self._parse_with_regex(response_text, max_colors)
```

### Phase 2 Deliverables Checklist

- [ ] ORM relationships on all models
- [ ] Cascade delete policies
- [ ] Eager loading queries for common patterns
- [ ] Redis caching for project colors
- [ ] Redis caching for AI extractions
- [ ] API usage logging model and migration
- [ ] Cost tracking service
- [ ] Cost reporting endpoint
- [ ] Claude JSON mode update
- [ ] Pydantic validation for AI responses

---

### Phase 3: Advanced Features and Monitoring (Week 4-5)

**Effort**: 40-50 hours
**Risk**: Medium (new capabilities)

#### Security Headers Middleware

```python
# Task 3.1: Add security headers
# File: src/copy_that/interfaces/api/middleware/security_headers.py
# See 03-security-hardening.md for implementation
```

#### Audit Logging

```python
# Task 3.2: Implement audit logging
# File: src/copy_that/infrastructure/security/audit_logger.py

import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.models import AuditLog

class AuditLogger:
    """Security audit logging"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger("audit")

    async def log(
        self,
        action: str,
        user_id: str,
        resource_type: str,
        resource_id: str,
        details: dict = None,
        ip_address: str = None
    ):
        """Log an auditable action"""

        log_entry = AuditLog(
            timestamp=datetime.utcnow(),
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address
        )

        self.db.add(log_entry)
        await self.db.commit()

        # Also log to file/stdout
        self.logger.info(
            f"AUDIT: {action} | user={user_id} | "
            f"resource={resource_type}:{resource_id} | "
            f"ip={ip_address}"
        )

    async def log_auth_success(self, user_id: str, ip_address: str):
        await self.log("AUTH_SUCCESS", user_id, "session", "new", ip_address=ip_address)

    async def log_auth_failure(self, email: str, ip_address: str):
        await self.log(
            "AUTH_FAILURE", "anonymous", "session", "failed",
            details={"email": email}, ip_address=ip_address
        )

    async def log_resource_access(
        self, user_id: str, resource_type: str, resource_id: str, action: str
    ):
        await self.log(f"{resource_type.upper()}_{action}", user_id, resource_type, resource_id)
```

#### Prometheus Metrics

```python
# Task 3.3: Add Prometheus metrics
# File: src/copy_that/infrastructure/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge, Info

# Application info
app_info = Info('copythat', 'Copy That application info')
app_info.info({
    'version': '1.0.0',
    'environment': os.getenv('ENVIRONMENT', 'local')
})

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1]
)

db_pool_size = Gauge(
    'db_pool_connections',
    'Database pool connections',
    ['state']
)

# AI metrics
ai_extraction_total = Counter(
    'ai_extraction_total',
    'Total AI extractions',
    ['model', 'status']
)

ai_extraction_duration = Histogram(
    'ai_extraction_duration_seconds',
    'AI extraction duration',
    ['model']
)

ai_tokens_used = Counter(
    'ai_tokens_used_total',
    'Total AI tokens used',
    ['model', 'type']
)

ai_cost_usd = Counter(
    'ai_cost_usd_total',
    'Total AI cost in USD',
    ['model']
)

# Cache metrics
cache_operations = Counter(
    'cache_operations_total',
    'Cache operations',
    ['operation', 'result']
)

# Rate limiting metrics
rate_limit_hits = Counter(
    'rate_limit_hits_total',
    'Rate limit hits',
    ['limit_type']
)
```

```python
# Task 3.4: Add metrics middleware
# File: src/copy_that/interfaces/api/middleware/metrics.py

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from ...infrastructure.monitoring.metrics import (
    http_requests_total,
    http_request_duration
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect HTTP request metrics"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status = response.status_code

        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

        http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        return response
```

#### Health Check Endpoints

```python
# Task 3.5: Comprehensive health checks
# File: src/copy_that/interfaces/api/health.py

from fastapi import APIRouter, Depends
from sqlalchemy import text
from redis.asyncio import Redis

router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    """Basic health check"""
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Readiness check - verify all dependencies"""
    checks = {}

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    # Redis check
    try:
        await redis.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"

    # Overall status
    all_healthy = all(v == "healthy" for v in checks.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks
    }

@router.get("/health/live")
async def liveness():
    """Liveness check - is the process alive"""
    return {"status": "alive"}

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### Phase 3 Deliverables Checklist

- [ ] Security headers middleware
- [ ] Secure error handling middleware
- [ ] Audit logging system
- [ ] Prometheus metrics
- [ ] Metrics middleware
- [ ] Health check endpoints (health, ready, live)
- [ ] Metrics endpoint for Prometheus scraping
- [ ] Database connection metrics
- [ ] AI usage metrics
- [ ] Cache hit/miss metrics

---

## 2. Testing Strategy

### 2.1 Unit Test Requirements

```python
# tests/unit/test_authentication.py

import pytest
from datetime import datetime, timedelta
from copy_that.infrastructure.security.authentication import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    get_password_hash
)

class TestPasswordHashing:
    def test_hash_password(self):
        password = "secure_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50

    def test_verify_correct_password(self):
        password = "secure_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        password = "secure_password_123"
        hashed = get_password_hash(password)

        assert verify_password("wrong_password", hashed) is False

class TestJWTTokens:
    def test_create_access_token(self):
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 50

    def test_decode_valid_token(self):
        data = {"sub": "user123", "email": "test@example.com", "roles": ["user"]}
        token = create_access_token(data)

        decoded = decode_token(token)

        assert decoded.user_id == "user123"
        assert decoded.email == "test@example.com"
        assert "user" in decoded.roles

    def test_decode_expired_token(self):
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        with pytest.raises(HTTPException) as exc:
            decode_token(token)

        assert exc.value.status_code == 401

    def test_create_token_pair(self):
        pair = create_token_pair("user123", "test@example.com", ["user"])

        assert pair.access_token
        assert pair.refresh_token
        assert pair.token_type == "bearer"
```

```python
# tests/unit/test_rate_limiter.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from copy_that.infrastructure.security.rate_limiter import RateLimiter

class TestRateLimiter:
    @pytest.fixture
    def mock_redis(self):
        redis = AsyncMock()
        redis.pipeline.return_value = AsyncMock()
        return redis

    @pytest.mark.asyncio
    async def test_first_request_allowed(self, mock_redis):
        # Setup pipeline mock
        pipe = mock_redis.pipeline.return_value
        pipe.execute.return_value = [None, 0, None, None]

        limiter = RateLimiter(mock_redis)
        allowed, remaining, reset = await limiter.check_rate_limit("test", 10, 60)

        assert allowed is True
        assert remaining == 9

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, mock_redis):
        pipe = mock_redis.pipeline.return_value
        pipe.execute.return_value = [None, 10, None, None]  # 10 requests already

        limiter = RateLimiter(mock_redis)
        allowed, remaining, reset = await limiter.check_rate_limit("test", 10, 60)

        assert allowed is False
        assert remaining == 0
```

```python
# tests/unit/test_input_validation.py

import pytest
from pydantic import ValidationError
from copy_that.interfaces.api.schemas import ExtractColorsRequest

class TestExtractColorsValidation:
    def test_valid_url_request(self):
        request = ExtractColorsRequest(
            project_id=1,
            image_url="https://example.com/image.png",
            max_colors=10
        )
        assert request.image_url == "https://example.com/image.png"

    def test_blocked_localhost_url(self):
        with pytest.raises(ValidationError) as exc:
            ExtractColorsRequest(
                project_id=1,
                image_url="http://localhost:8000/image.png"
            )
        assert "URL host not allowed" in str(exc.value)

    def test_blocked_internal_ip(self):
        with pytest.raises(ValidationError) as exc:
            ExtractColorsRequest(
                project_id=1,
                image_url="http://192.168.1.1/image.png"
            )
        assert "URL host not allowed" in str(exc.value)

    def test_blocked_aws_metadata(self):
        with pytest.raises(ValidationError) as exc:
            ExtractColorsRequest(
                project_id=1,
                image_url="http://169.254.169.254/latest/meta-data"
            )
        assert "URL host not allowed" in str(exc.value)

    def test_max_colors_bounds(self):
        # Too few
        with pytest.raises(ValidationError):
            ExtractColorsRequest(project_id=1, image_url="https://x.com/i.png", max_colors=0)

        # Too many
        with pytest.raises(ValidationError):
            ExtractColorsRequest(project_id=1, image_url="https://x.com/i.png", max_colors=100)

    def test_base64_size_limit(self):
        # Create oversized base64 (>14MB)
        huge_data = "A" * (15 * 1024 * 1024)

        with pytest.raises(ValidationError) as exc:
            ExtractColorsRequest(
                project_id=1,
                image_base64=huge_data
            )
        assert "too large" in str(exc.value)
```

### 2.2 Integration Test Scenarios

```python
# tests/integration/test_auth_flow.py

import pytest
from httpx import AsyncClient
from copy_that.interfaces.api.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

class TestAuthenticationFlow:
    @pytest.mark.asyncio
    async def test_register_user(self, client):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_login_success(self, client, registered_user):
        response = await client.post("/api/v1/auth/token", data={
            "username": "test@example.com",
            "password": "TestPass123!"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client, registered_user):
        response = await client.post("/api/v1/auth/token", data={
            "username": "test@example.com",
            "password": "WrongPassword"
        })

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_protected_endpoint(self, client, auth_headers):
        response = await client.get(
            "/api/v1/projects",
            headers=auth_headers
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_access_without_auth(self, client):
        response = await client.get("/api/v1/projects")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token(self, client, tokens):
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
```

```python
# tests/integration/test_color_extraction.py

class TestColorExtraction:
    @pytest.mark.asyncio
    async def test_extract_from_url(self, client, auth_headers, project):
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": project.id,
                "image_url": "https://example.com/test-image.png",
                "max_colors": 5
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["colors"]) == 5
        assert all("hex" in c for c in data["colors"])

    @pytest.mark.asyncio
    async def test_extract_unauthorized_project(self, client, auth_headers, other_user_project):
        response = await client.post(
            "/api/v1/colors/extract",
            json={
                "project_id": other_user_project.id,
                "image_url": "https://example.com/test.png"
            },
            headers=auth_headers
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, client, auth_headers, project):
        # Make 11 requests (limit is 10/minute)
        for i in range(11):
            response = await client.post(
                "/api/v1/colors/extract",
                json={
                    "project_id": project.id,
                    "image_url": f"https://example.com/image{i}.png"
                },
                headers=auth_headers
            )

            if i < 10:
                assert response.status_code == 200
            else:
                assert response.status_code == 429
                assert "Retry-After" in response.headers
```

### 2.3 Security Test Cases

```python
# tests/security/test_vulnerabilities.py

class TestSecurityVulnerabilities:
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, client, auth_headers):
        """Verify SQLAlchemy ORM prevents SQL injection"""
        response = await client.get(
            "/api/v1/projects",
            params={"name": "'; DROP TABLE projects; --"},
            headers=auth_headers
        )

        # Should not error or affect database
        assert response.status_code in (200, 400)

    @pytest.mark.asyncio
    async def test_xss_in_project_name(self, client, auth_headers):
        """Verify XSS payloads are rejected or sanitized"""
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "<script>alert('xss')</script>",
                "description": "Test"
            },
            headers=auth_headers
        )

        # Should reject or sanitize
        if response.status_code == 200:
            data = response.json()
            assert "<script>" not in data["name"]
        else:
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ssrf_blocked(self, client, auth_headers, project):
        """Verify internal URLs are blocked"""
        blocked_urls = [
            "http://localhost/admin",
            "http://127.0.0.1:8080/secret",
            "http://169.254.169.254/latest/meta-data",
            "http://192.168.1.1/router",
            "http://10.0.0.1/internal",
        ]

        for url in blocked_urls:
            response = await client.post(
                "/api/v1/colors/extract",
                json={"project_id": project.id, "image_url": url},
                headers=auth_headers
            )

            assert response.status_code == 422, f"SSRF not blocked for {url}"

    @pytest.mark.asyncio
    async def test_jwt_tampering_rejected(self, client):
        """Verify tampered JWTs are rejected"""
        # Valid token structure but invalid signature
        tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIn0.tampered"

        response = await client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_cors_preflight(self, client):
        """Verify CORS preflight returns correct headers"""
        response = await client.options(
            "/api/v1/projects",
            headers={
                "Origin": "https://copythat.dev",
                "Access-Control-Request-Method": "GET"
            }
        )

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
```

### 2.4 Performance Test Framework

```python
# tests/performance/locustfile.py

from locust import HttpUser, task, between, events
import random

class CopyThatUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login and get token"""
        response = self.client.post("/api/v1/auth/token", data={
            "username": f"loadtest{random.randint(1, 100)}@example.com",
            "password": "LoadTest123!"
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
            self.project_id = self._create_project()
        else:
            self.headers = {}
            self.project_id = None

    def _create_project(self):
        response = self.client.post(
            "/api/v1/projects",
            json={"name": f"Load Test {random.randint(1, 10000)}"},
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()["id"]
        return None

    @task(5)
    def list_projects(self):
        """Most common: list projects"""
        self.client.get("/api/v1/projects", headers=self.headers)

    @task(3)
    def get_project_colors(self):
        """Common: get colors for a project"""
        if self.project_id:
            self.client.get(
                f"/api/v1/projects/{self.project_id}/colors",
                headers=self.headers
            )

    @task(1)
    def extract_colors(self):
        """Expensive: extract colors from image"""
        if self.project_id:
            self.client.post(
                "/api/v1/colors/extract",
                json={
                    "project_id": self.project_id,
                    "image_url": "https://picsum.photos/800/600",
                    "max_colors": 10
                },
                headers=self.headers
            )


# Run with: locust -f tests/performance/locustfile.py
```

---

## 3. Monitoring & Observability

### 3.1 Logging Strategy

```python
# src/copy_that/infrastructure/logging_config.py

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "project_id"):
            log_data["project_id"] = record.project_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def configure_logging():
    """Configure application logging"""

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Specific loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Audit logger (always enabled)
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)

    return root_logger
```

### 3.2 Database Performance Metrics

```python
# src/copy_that/infrastructure/database.py

from sqlalchemy import event
from prometheus_client import Histogram
import time

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

def setup_query_instrumentation(engine):
    """Add query timing instrumentation"""

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info["query_start_time"].pop()

        # Determine query type
        query_type = statement.split()[0].upper() if statement else "UNKNOWN"

        db_query_duration.labels(query_type=query_type).observe(total)

        # Log slow queries
        if total > 0.1:  # 100ms
            logging.warning(
                f"Slow query ({total:.3f}s): {statement[:100]}..."
            )
```

### 3.3 Cost Tracking Dashboard

```python
# src/copy_that/interfaces/api/admin.py

from fastapi import APIRouter, Depends
from ...application.cost_tracker import CostTracker
from ...infrastructure.security.authentication import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get(
    "/costs",
    dependencies=[Depends(require_roles("admin"))]
)
async def get_cost_dashboard(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get AI cost dashboard data"""
    tracker = CostTracker(db)
    report = await tracker.get_cost_report(days)

    return {
        "period_days": days,
        "total_cost_usd": round(report["total_cost"], 2),
        "daily_average_usd": round(report["total_cost"] / days, 2),
        "by_model": report["by_model"],
        "cache_savings_usd": round(report["cache_savings"], 2),
        "cache_savings_percentage": round(
            report["cache_savings"] / max(report["total_cost"], 0.01) * 100, 1
        )
    }

@router.get(
    "/costs/daily",
    dependencies=[Depends(require_roles("admin"))]
)
async def get_daily_costs(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get daily cost breakdown"""
    result = await db.execute(
        select(
            func.date(APIUsageLog.timestamp).label("date"),
            func.sum(APIUsageLog.cost_usd).label("cost"),
            func.count(APIUsageLog.id).label("requests")
        )
        .where(APIUsageLog.timestamp >= datetime.utcnow() - timedelta(days=days))
        .group_by(func.date(APIUsageLog.timestamp))
        .order_by(func.date(APIUsageLog.timestamp))
    )

    return [
        {"date": str(row.date), "cost": round(row.cost, 2), "requests": row.requests}
        for row in result.all()
    ]
```

### 3.4 Alerting Thresholds

```yaml
# prometheus/alerts.yml

groups:
  - name: copythat
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} requests/second"

      # Slow requests
      - alert: SlowRequests
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow request p99"
          description: "p99 latency is {{ $value }}s"

      # Database pool exhaustion
      - alert: DatabasePoolExhausted
        expr: db_pool_connections{state="overflow"} > 15
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database pool exhausted"

      # High AI costs
      - alert: HighAICost
        expr: increase(ai_cost_usd_total[1h]) > 10
        for: 0m
        labels:
          severity: warning
        annotations:
          summary: "High AI cost"
          description: "Spent ${{ $value }} in the last hour"

      # Rate limiting triggered
      - alert: RateLimitingTriggered
        expr: rate(rate_limit_hits_total[5m]) > 1
        for: 5m
        labels:
          severity: info
        annotations:
          summary: "Rate limiting active"
```

---

## 4. Migration Scripts

### 4.1 Database Migration Sequence

```bash
# Run migrations in order
alembic upgrade head

# Or run specific migrations
alembic upgrade 2025_11_22_auth      # Authentication tables
alembic upgrade 2025_11_22_indexes   # Performance indexes
alembic upgrade 2025_11_22_audit     # Audit logging
alembic upgrade 2025_11_22_costs     # Cost tracking
```

### 4.2 Secret Migration Script

```python
# scripts/migrate_secrets_to_gcp.py

"""
Migrate secrets from hardcoded config to GCP Secret Manager

Usage:
    python scripts/migrate_secrets_to_gcp.py --project copy-that-platform --env staging
"""

import argparse
from google.cloud import secretmanager

def create_secret(client, project_id, secret_id, secret_value):
    """Create or update a secret in Secret Manager"""
    parent = f"projects/{project_id}"

    # Check if secret exists
    try:
        client.get_secret(request={"name": f"{parent}/secrets/{secret_id}"})
        print(f"Secret {secret_id} exists, adding new version")
    except Exception:
        # Create secret
        client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}}
            }
        )
        print(f"Created secret {secret_id}")

    # Add secret version
    client.add_secret_version(
        request={
            "parent": f"{parent}/secrets/{secret_id}",
            "payload": {"data": secret_value.encode()}
        }
    )
    print(f"Added new version for {secret_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--env", required=True, choices=["staging", "production"])
    args = parser.parse_args()

    client = secretmanager.SecretManagerServiceClient()

    # Secrets to migrate (get from environment or prompt)
    secrets = {
        "database-url": input("Enter DATABASE_URL: "),
        "redis-url": input("Enter REDIS_URL: "),
        "jwt-secret-key": input("Enter SECRET_KEY: "),
        "anthropic-api-key": input("Enter ANTHROPIC_API_KEY: "),
        "openai-api-key": input("Enter OPENAI_API_KEY: "),
    }

    for secret_id, value in secrets.items():
        if value:
            create_secret(client, args.project, f"{args.env}-{secret_id}", value)

    print("\nMigration complete!")
    print("Update your Cloud Run service to use these secrets.")


if __name__ == "__main__":
    main()
```

### 4.3 Data Backfill Script

```python
# scripts/backfill_user_ownership.py

"""
Backfill owner_id for existing projects after adding authentication.

Usage:
    python scripts/backfill_user_ownership.py --default-user admin@example.com
"""

import asyncio
from sqlalchemy import select, update
from copy_that.infrastructure.database import AsyncSessionLocal
from copy_that.domain.models import User, Project

async def backfill_ownership(default_email: str):
    async with AsyncSessionLocal() as db:
        # Get default user
        result = await db.execute(
            select(User).where(User.email == default_email)
        )
        default_user = result.scalar_one_or_none()

        if not default_user:
            print(f"Creating default admin user: {default_email}")
            default_user = User(
                email=default_email,
                hashed_password=get_password_hash("ChangeMeImmediately!"),
                is_superuser=True,
                roles=["admin", "user"]
            )
            db.add(default_user)
            await db.flush()

        # Update projects without owner
        result = await db.execute(
            update(Project)
            .where(Project.owner_id.is_(None))
            .values(owner_id=default_user.id)
            .returning(Project.id)
        )
        updated = result.all()

        await db.commit()
        print(f"Updated {len(updated)} projects with owner {default_email}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--default-user", required=True)
    args = parser.parse_args()

    asyncio.run(backfill_ownership(args.default_user))
```

---

## Summary

### Implementation Timeline

| Phase | Duration | Focus | Outcome |
|-------|----------|-------|---------|
| Phase 1 | Week 1 | Security + Quick Wins | Production-ready security |
| Phase 2 | Week 2-3 | Database + AI Costs | Performance optimized |
| Phase 3 | Week 4-5 | Monitoring + Advanced | Observable system |

### Success Metrics

| Metric | Current | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|---------|
| Security Score | 4/10 | 7/10 | 8/10 | 9/10 |
| Database Performance | 6/10 | 7.5/10 | 8.5/10 | 9/10 |
| AI Cost Visibility | 0/10 | 3/10 | 8/10 | 9/10 |
| Test Coverage | 75% | 80% | 85% | 90% |
| Observability | 2/10 | 4/10 | 7/10 | 9/10 |

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing API clients | Version API endpoints, maintain backwards compatibility |
| Data loss during migration | Backup before each migration, test in staging first |
| Performance regression | Load test after each phase, rollback plan ready |
| Security vulnerabilities | Security scan before each deployment |

---

*Return to [README.md](./README.md)*
