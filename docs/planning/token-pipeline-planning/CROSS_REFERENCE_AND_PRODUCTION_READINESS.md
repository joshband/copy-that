# Cross-Reference and Production Readiness Document

**Version:** 1.0 | **Date:** 2025-11-22 | **Status:** Planning Document

This document synthesizes all token pipeline planning documentation across branches, providing a unified view of dependencies, implementation timelines, and production readiness requirements.

---

## 1. Executive Summary

### Overview of Planning Documentation

The Copy That token pipeline implementation spans **four concurrent planning branches**, each addressing different aspects of the system:

| Branch | Focus Area | Key Deliverables |
|--------|------------|------------------|
| **Current (Spacing Token)** | Token Pipeline Core | Spacing token models, extractors, aggregators, API endpoints |
| **Backend Optimization** | Performance & Security | Authentication, rate limiting, caching, cost tracking |
| **CV Preprocessing** | Image Processing | Async loading, validation, OpenCV preprocessing, optimization |
| **Frontend Infrastructure** | UI Performance & DevOps | React optimization, CI/CD hardening, monitoring |

### Key Dependencies Between Components

```
                    ┌─────────────────────┐
                    │   Frontend Client   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   API Gateway       │
                    │  (Rate Limiting)    │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌────────────────┐
│ Auth Service  │    │ Token Pipeline  │    │ Export Service │
│ (JWT/APIKey)  │    │ (Extract/Agg)   │    │ (W3C/CSS/etc)  │
└───────────────┘    └────────┬────────┘    └────────────────┘
                              │
               ┌──────────────┼──────────────┐
               │              │              │
               ▼              ▼              ▼
      ┌─────────────┐  ┌────────────┐  ┌───────────┐
      │ CV Pipeline │  │  AI APIs   │  │ Database  │
      │ (OpenCV)    │  │ (Claude)   │  │ (Postgres)│
      └─────────────┘  └────────────┘  └─────┬─────┘
                                             │
                                       ┌─────▼─────┐
                                       │   Redis   │
                                       │  (Cache)  │
                                       └───────────┘
```

### Critical Path Dependencies

1. **Authentication (Backend)** must complete before Token Pipeline can secure endpoints
2. **CV Preprocessing** must complete before Token Pipeline can accept images efficiently
3. **Token Factory** provides base classes for Spacing Token implementation
4. **Frontend Store** must be optimized before handling large token sets

---

## 2. Information Influence Path Diagram

### Documentation Flow Between Branches

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION INFLUENCE PATHS                         │
└─────────────────────────────────────────────────────────────────────────┘

                    TOKEN_FACTORY_PLANNING.md
                              │
                              │ provides base abstractions for
                              ▼
                    SPACING_TOKEN_PIPELINE_PLANNING.md
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    CV Pipeline          Backend Opt        Frontend Infra
    Roadmap              Roadmap            Roadmap
          │                   │                   │
          │                   │                   │
          │ image processing  │ security &        │ UI patterns &
          │ patterns          │ caching           │ store design
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
                    PRODUCTION DEPLOYMENT
                    (This Document)


┌─────────────────────────────────────────────────────────────────────────┐
│                    SPECIFIC INFLUENCES                                   │
└─────────────────────────────────────────────────────────────────────────┘

Backend Optimization ────► Token Pipeline
  • Redis caching patterns for extraction results
  • JWT authentication for API endpoints
  • Rate limiting middleware
  • Cost tracking for AI calls

CV Preprocessing ────► Token Pipeline
  • AsyncImageFetcher replaces requests.get()
  • ImageValidator provides format checking
  • ImagePreprocessor optimizes for AI extraction
  • SSRF protection for URL inputs

Frontend Infrastructure ────► Token Pipeline
  • Token store patterns (Zustand optimization)
  • TokenCard memoization for performance
  • Virtual scrolling for large token sets
  • E2E test patterns for token workflows

Token Factory ────► All Token Types
  • BaseToken, BaseExtractor, BaseAggregator classes
  • Registry system for plugin architecture
  • Pipeline orchestrator pattern
  • Generator mixins for exports
```

### Cross-Document References

| Source Document | Influenced By | Influences |
|-----------------|---------------|------------|
| SPACING_TOKEN_PIPELINE_PLANNING | TOKEN_FACTORY_PLANNING | Backend API design, Frontend store |
| TOKEN_FACTORY_PLANNING | Existing color implementation | All future token types |
| Backend 04-implementation-roadmap | Security best practices | All API endpoints |
| CV 07-implementation-roadmap | Python async patterns | Image extraction endpoints |
| Frontend 05-implementation-roadmap | React performance patterns | Token visualization components |

---

## 3. Cross-Reference Matrix

### Component Mapping

| Component | Source Branch | Key Decisions | Dependencies |
|-----------|---------------|---------------|--------------|
| **SpacingToken Model** | Current | Pydantic + SQLAlchemy hybrid, W3C-compliant fields | Token Factory BaseToken |
| **AISpacingExtractor** | Current | Claude Sonnet 4.5, JSON mode, 12 tokens max | Backend cost tracking, CV preprocessing |
| **SpacingAggregator** | Current | 10% threshold deduplication, provenance tracking | Token Factory BaseAggregator |
| **Authentication** | Backend | JWT + API Keys, bcrypt hashing | GCP Secret Manager |
| **Rate Limiting** | Backend | Redis-based, 60/min 1000/hr | Redis HA setup |
| **Cost Tracking** | Backend | APIUsageLog model, per-model pricing | Database migration |
| **AsyncImageFetcher** | CV | httpx with SSRF protection | None (foundation) |
| **ImagePreprocessor** | CV | OpenCV CLAHE, LANCZOS4 resize | AsyncImageFetcher |
| **ConcurrentImageProcessor** | CV | Semaphore-controlled batching | ImagePreprocessor |
| **TokenGrid Virtualization** | Frontend | @tanstack/react-virtual | Zustand store optimization |
| **React Memoization** | Frontend | React.memo on TokenCard et al | TypeScript strict mode |
| **CI/CD Pipeline** | Frontend | Matrix jobs, Docker cache, test sharding | Security scan enforcement |

### API Endpoint Mapping

| Endpoint | Defined In | Security | Caching | Dependencies |
|----------|------------|----------|---------|--------------|
| `POST /api/v1/spacing/extract` | SPACING_TOKEN_PIPELINE | JWT auth | Redis (image hash) | CV Pipeline, AI API |
| `POST /api/v1/spacing/extract-streaming` | SPACING_TOKEN_PIPELINE | JWT auth | None | SSE, CV Pipeline |
| `POST /api/v1/spacing/extract-batch` | SPACING_TOKEN_PIPELINE | JWT auth | Aggregation cache | Semaphore, CV Pipeline |
| `POST /api/v1/auth/login` | Backend Roadmap | Public | None | User model, bcrypt |
| `GET /health/ready` | Backend Roadmap | Public | None | DB, Redis connectivity |
| `GET /metrics` | Backend Roadmap | Internal | None | Prometheus client |

---

## 4. Implementation Plan Synthesis

### Unified Timeline (8 Weeks)

#### Phase 1: Foundation (Weeks 1-2)

**Goals:** Security foundation, CV infrastructure, Token Factory core

| Week | Backend Optimization | CV Preprocessing | Token Pipeline | Frontend Infrastructure |
|------|---------------------|------------------|----------------|------------------------|
| 1 | User/APIKey models, Auth router, GCP Secrets | Dependencies, Module structure, Async loading | Factory directory structure, BaseToken class | Security scans, TypeScript strict |
| 2 | Connection pool (20), Basic rate limiting, Critical indexes | Basic validation, Unit tests | BaseExtractor, BaseAggregator, Registry | React.memo, Database tier upgrade |

**Key Deliverables:**
- [ ] JWT authentication working
- [ ] Secrets in GCP Secret Manager
- [ ] CV async loading operational
- [ ] Token Factory base classes complete
- [ ] CI blocks on security issues

---

#### Phase 2: Core Features (Weeks 3-4)

**Goals:** Full preprocessing pipeline, Spacing token implementation, AI optimization

| Week | Backend Optimization | CV Preprocessing | Token Pipeline | Frontend Infrastructure |
|------|---------------------|------------------|----------------|------------------------|
| 3 | ORM relationships, Redis caching layer | OpenCV preprocessor, Image optimizer | SpacingToken model, AISpacingExtractor | Code splitting, Budget alerts |
| 4 | Claude JSON mode, Cost tracking | Pipeline orchestrator, Application service | SpacingAggregator, Batch processing | List virtualization, Staging auth |

**Key Deliverables:**
- [ ] Redis caching for extractions
- [ ] CV pipeline processing images
- [ ] Spacing extraction working end-to-end
- [ ] AI cost tracking operational
- [ ] Virtual scrolling for tokens

---

#### Phase 3: Integration (Weeks 5-6)

**Goals:** API endpoints, Database persistence, Export generators

| Week | Backend Optimization | CV Preprocessing | Token Pipeline | Frontend Infrastructure |
|------|---------------------|------------------|----------------|------------------------|
| 5 | Security headers, Audit logging | Memory optimization, Circuit breaker | API router endpoints, SSE streaming | CI optimization, Store split |
| 6 | Prometheus metrics, Health checks | Caching layer, Integration tests | Export generators (W3C, CSS, React) | Bundle optimization, Automated rollback |

**Key Deliverables:**
- [ ] All API endpoints secured and rate-limited
- [ ] Full observability with Prometheus
- [ ] All export formats working
- [ ] Automated deployment with rollback
- [ ] CI < 10 minutes

---

#### Phase 4: Production Hardening (Weeks 7-8)

**Goals:** Testing, documentation, performance validation

| Week | Backend Optimization | CV Preprocessing | Token Pipeline | Frontend Infrastructure |
|------|---------------------|------------------|----------------|------------------------|
| 7 | Load testing, Migration scripts | Performance testing, Documentation | Database migration, Frontend integration | Cloud Monitoring alerts, Redis HA |
| 8 | DR procedures, Runbooks | Production hardening | Full E2E testing | Test coverage >80%, E2E suite |

**Key Deliverables:**
- [ ] Load tested at 10 requests/second
- [ ] All documentation complete
- [ ] E2E tests covering critical paths
- [ ] Redis HA enabled
- [ ] Production monitoring active

---

### Critical Path Analysis

```
Week 1 ──► Week 2 ──► Week 3 ──► Week 4 ──► Week 5 ──► Week 6 ──► Week 7 ──► Week 8
  │          │          │          │          │          │          │          │
  │          │          │          │          │          │          │          │
Auth      Index      Redis      Batch      API       Export    E2E       Prod
Models    Create     Cache      Extract    Router    Gens      Tests     Deploy

Critical Path: Auth ► Redis ► SpacingExtractor ► API ► Export ► E2E
```

---

## 5. Deployment Strategy

### Docker/Cloud Run Configuration

#### Dockerfile Updates Required

```dockerfile
# Base image with system dependencies
FROM python:3.12-slim as base

# System dependencies for CV pipeline
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[prod]"

# Copy application
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

# Run migrations on startup
CMD ["sh", "-c", "alembic upgrade head && uvicorn copy_that.main:app --host 0.0.0.0 --port $PORT"]
```

#### Cloud Run Service Configuration

```yaml
# cloud-run-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: copy-that-api
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"  # For AI processing
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
        - image: gcr.io/PROJECT_ID/copy-that-api:TAG
          resources:
            limits:
              cpu: "2"
              memory: "2Gi"
          env:
            - name: ENVIRONMENT
              value: production
            - name: PORT
              value: "8080"
          startupProbe:
            httpGet:
              path: /health
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health/live
```

### Environment Variables

| Variable | Description | Source | Required |
|----------|-------------|--------|----------|
| `DATABASE_URL` | PostgreSQL connection | GCP Secret Manager | Yes |
| `REDIS_URL` | Redis connection | GCP Secret Manager | Yes |
| `SECRET_KEY` | JWT signing key | GCP Secret Manager | Yes |
| `ANTHROPIC_API_KEY` | Claude API key | GCP Secret Manager | Yes |
| `OPENAI_API_KEY` | OpenAI API key | GCP Secret Manager | No |
| `ENVIRONMENT` | Deployment environment | Cloud Run env | Yes |
| `PORT` | Server port | Cloud Run env | Yes |
| `MAX_CONCURRENT_EXTRACTIONS` | Semaphore limit | Config | No (default: 5) |
| `REDIS_CACHE_TTL` | Cache TTL seconds | Config | No (default: 3600) |

### Database Migrations

#### Required Migrations (in order)

1. **add_user_authentication** (Backend Week 1)
   - Creates `users` and `api_keys` tables
   - Adds `owner_id` to `projects`

2. **add_performance_indexes** (Backend Week 1)
   - Creates indexes on `color_tokens`, `extraction_jobs`

3. **add_api_usage_logs** (Backend Week 4)
   - Creates `api_usage_logs` table for cost tracking

4. **add_spacing_tokens** (Token Pipeline Week 3)
   - Creates `spacing_tokens` table
   - All foreign keys and indexes

5. **add_audit_logs** (Backend Week 5)
   - Creates `audit_logs` table

#### Migration Execution

```bash
# Run all pending migrations
alembic upgrade head

# Check current version
alembic current

# Generate new migration
alembic revision --autogenerate -m "description"

# Rollback one version
alembic downgrade -1
```

### Redis/Caching Setup

#### Redis Instance Configuration

```hcl
# Terraform configuration
resource "google_redis_instance" "main" {
  name           = "copy-that-redis-prod"
  tier           = "STANDARD_HA"  # High availability
  memory_size_gb = 5
  region         = "us-central1"
  replica_count  = 1

  redis_configs = {
    "maxmemory-policy" = "allkeys-lru"
  }

  maintenance_policy {
    weekly_maintenance_window {
      day        = "SUNDAY"
      start_time { hours = 3 }
    }
  }
}
```

#### Cache Key Patterns

| Pattern | Purpose | TTL |
|---------|---------|-----|
| `copythat:colors:project:{id}` | Project color tokens | 1 hour |
| `copythat:colors:extraction:{hash}` | AI extraction results | 24 hours |
| `copythat:spacing:project:{id}` | Project spacing tokens | 1 hour |
| `copythat:spacing:extraction:{hash}` | Spacing extraction results | 24 hours |
| `copythat:ratelimit:{user}:{window}` | Rate limit counters | 1 minute/hour |
| `copythat:session:{token}` | User session data | 30 minutes |

---

## 6. Integration Points

### Backend <-> Frontend Integration

#### API Contract

```typescript
// Frontend types matching backend schemas
interface SpacingToken {
  id: number;
  value_px: number;
  value_rem: number;
  value_em: number;
  scale: string;
  base_unit: number;
  name: string;
  spacing_type: 'padding' | 'margin' | 'gap' | 'inset' | 'gutter';
  confidence: number;
  design_intent: string;
  is_grid_compliant: boolean;
  semantic_names: {
    simple: string;
    descriptive: string;
    contextual: string;
    scale_position: string;
  };
}

interface SpacingExtractionRequest {
  image_data: string;  // Base64
  media_type: string;
  max_spacing?: number;
  project_id?: number;
}

interface SpacingExtractionResponse {
  job_id: number;
  tokens: SpacingToken[];
  statistics: {
    token_count: number;
    base_unit_detected: number;
    rhythm_consistency: string;
  };
}
```

#### SSE Streaming Protocol

```typescript
// Frontend SSE handling
const eventSource = new EventSource('/api/v1/spacing/extract-streaming');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.status) {
    case 'starting':
      setPhase(1);
      break;
    case 'token_extracted':
      addToken(data.token);
      setProgress(data.progress);
      break;
    case 'computing_properties':
      setPhase(2);
      break;
    case 'extraction_complete':
      setTokens(data.tokens);
      setPhase(3);
      break;
    case 'error':
      setError(data.message);
      break;
  }
};
```

### Token Pipeline <-> CV Preprocessing Integration

```python
# Updated extraction using CV pipeline
from copy_that.application.services.image_service import ImageService
from copy_that.infrastructure.cv.preprocessing import ImageSource

class AISpacingExtractor:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = "claude-sonnet-4-5-20250929"
        self.image_service = ImageService()  # NEW: CV integration

    async def extract_spacing_from_image_url(
        self,
        image_url: str,
        max_spacing: int = 12
    ) -> SpacingExtractionResult:
        # Use CV pipeline instead of raw requests.get()
        source = ImageSource.from_url(image_url)
        processed = await self.image_service.preprocess_for_extraction(source)

        # Get base64 for AI API
        base64_data, media_type = self.image_service.get_base64_for_api(processed)

        return await self.extract_spacing_from_base64(
            base64_data,
            media_type,
            max_spacing
        )
```

### Database <-> Caching Integration

```python
# Cache-through pattern for token retrieval
class SpacingTokenRepository:
    def __init__(self, db: AsyncSession, cache: ColorCacheService):
        self.db = db
        self.cache = cache

    async def get_project_spacing(self, project_id: int) -> list[SpacingToken]:
        # Try cache first
        cached = await self.cache.get_project_spacing(project_id)
        if cached:
            return [SpacingToken(**t) for t in cached]

        # Query database
        result = await self.db.execute(
            select(SpacingTokenModel)
            .where(SpacingTokenModel.project_id == project_id)
            .order_by(SpacingTokenModel.value_px)
        )
        tokens = result.scalars().all()

        # Cache for next time
        await self.cache.set_project_spacing(
            project_id,
            [t.to_dict() for t in tokens]
        )

        return tokens

    async def create_spacing_tokens(
        self,
        project_id: int,
        tokens: list[SpacingToken]
    ):
        # Create in database
        for token in tokens:
            db_token = SpacingTokenModel(**token.dict(), project_id=project_id)
            self.db.add(db_token)

        await self.db.commit()

        # Invalidate cache
        await self.cache.invalidate_project_spacing(project_id)
```

---

## 7. Testing Strategy (Unified)

### Unit Testing Patterns

#### From Token Pipeline

```python
# tests/unit/tokens/spacing/test_aggregator.py
class TestSpacingAggregator:
    def test_aggregate_batch_deduplication(self):
        batch = [
            [{'value_px': 16, 'confidence': 0.9}],
            [{'value_px': 17, 'confidence': 0.85}],  # Within 10%
        ]

        library = SpacingAggregator.aggregate_batch(batch, 0.10)

        assert len(library.tokens) == 1
        assert library.tokens[0].occurrence_count == 2
```

#### From Backend Optimization

```python
# tests/unit/test_rate_limiter.py
class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, mock_redis):
        pipe = mock_redis.pipeline.return_value
        pipe.execute.return_value = [None, 10, None, None]  # At limit

        limiter = RateLimiter(mock_redis)
        allowed, remaining, reset = await limiter.check_rate_limit("test", 10, 60)

        assert allowed is False
        assert remaining == 0
```

#### From CV Preprocessing

```python
# tests/unit/test_image_processing/test_validator.py
class TestImageValidator:
    def test_rejects_non_image(self):
        with pytest.raises(UnsupportedFormatError):
            validator = ImageValidator()
            validator.validate(b"not an image")

    def test_detects_truncation(self):
        truncated_png = PNG_HEADER[:50]

        with pytest.raises(CorruptImageError):
            validator = IntegrityValidator()
            validator.check_truncation(truncated_png, ImageFormat.PNG)
```

### Integration Testing Patterns

#### Full Pipeline Integration

```python
# tests/integration/test_spacing_pipeline.py
class TestSpacingPipeline:
    @pytest.fixture
    async def setup(self, test_db, test_redis):
        # Create test project
        project = Project(name="Test", owner_id="user123")
        test_db.add(project)
        await test_db.commit()
        return project.id

    async def test_extraction_to_persistence(self, client, setup):
        project_id = setup

        # Extract
        response = await client.post(
            "/api/v1/spacing/extract",
            json={
                "image_data": load_test_image_base64(),
                "media_type": "image/png",
                "project_id": project_id
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tokens"]) > 0

        # Verify persistence
        tokens = await test_db.execute(
            select(SpacingToken).where(SpacingToken.project_id == project_id)
        )
        assert len(tokens.scalars().all()) > 0

        # Verify cache
        cached = await test_redis.get(f"copythat:spacing:project:{project_id}")
        assert cached is not None
```

### E2E Testing Patterns

#### From Frontend Infrastructure

```typescript
// e2e/spacing-extraction.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Spacing Extraction Workflow', () => {
  test('extracts spacing from uploaded image', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[name=email]', 'test@example.com');
    await page.fill('[name=password]', 'password');
    await page.click('button[type=submit]');

    // Navigate to extraction
    await page.goto('/projects/1/extract');

    // Upload image
    const fileInput = page.locator('input[type=file]');
    await fileInput.setInputFiles('fixtures/ui-screenshot.png');

    // Select spacing extraction
    await page.click('[data-testid=token-type-spacing]');

    // Start extraction
    await page.click('[data-testid=extract-button]');

    // Wait for streaming completion
    await expect(page.locator('[data-testid=extraction-phase]'))
      .toHaveText('Complete', { timeout: 30000 });

    // Verify tokens displayed
    const tokenCards = page.locator('[data-testid=spacing-token-card]');
    await expect(tokenCards).toHaveCount.greaterThan(0);

    // Verify token details
    const firstToken = tokenCards.first();
    await expect(firstToken.locator('.token-value')).toContainText('px');
    await expect(firstToken.locator('.token-scale')).toBeVisible();
  });

  test('exports spacing tokens to CSS', async ({ page }) => {
    // ... navigate to project with tokens

    await page.click('[data-testid=export-button]');
    await page.click('[data-testid=format-css]');

    const exportContent = await page.locator('[data-testid=export-preview]').textContent();
    expect(exportContent).toContain(':root {');
    expect(exportContent).toContain('--spacing-');
  });
});
```

### Performance/Load Testing

```python
# tests/performance/test_spacing_load.py
import asyncio
import statistics

class TestSpacingLoadPerformance:
    async def test_sustained_extraction_load(self, client, auth_token):
        """Process 100 extractions over 5 minutes"""
        durations = []
        errors = 0

        for i in range(100):
            start = time.time()
            try:
                response = await client.post(
                    "/api/v1/spacing/extract",
                    json={"image_data": test_image, "media_type": "image/png"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                if response.status_code != 200:
                    errors += 1
            except Exception:
                errors += 1

            duration = time.time() - start
            durations.append(duration)

            # Rate limit: 20/minute
            await asyncio.sleep(3)

        # Assertions
        p95 = sorted(durations)[int(len(durations) * 0.95)]
        assert p95 < 5.0, f"P95 latency {p95}s exceeds 5s target"
        assert errors / 100 < 0.05, f"Error rate {errors}% exceeds 5%"

        print(f"P50: {statistics.median(durations):.2f}s")
        print(f"P95: {p95:.2f}s")
        print(f"Error rate: {errors}%")

    async def test_batch_memory_stability(self, client, auth_token):
        """Verify no memory leaks during batch processing"""
        import psutil
        process = psutil.Process()

        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        for _ in range(10):
            await client.post(
                "/api/v1/spacing/extract-batch",
                json={"image_urls": [test_urls] * 10},
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory

        assert memory_growth < 100, f"Memory grew {memory_growth}MB during batch processing"
```

---

## 8. Production Readiness Checklist

### Security

- [ ] **Authentication implemented** (JWT + API Keys)
- [ ] **Authorization on all endpoints** (project ownership checks)
- [ ] **Rate limiting active** (60/min, 1000/hr per user)
- [ ] **SSRF protection enabled** (URL validation in CV pipeline)
- [ ] **Secrets in GCP Secret Manager** (no hardcoded credentials)
- [ ] **Security headers middleware** (CSP, HSTS, etc.)
- [ ] **Input validation** (Pydantic schemas on all endpoints)
- [ ] **SQL injection prevention** (parameterized queries via SQLAlchemy)
- [ ] **Audit logging** (all sensitive operations logged)
- [ ] **Security scans passing** (pip-audit, bandit, trivy)

### Database

- [ ] **All indexes created** (project_id, value_px, scale, etc.)
- [ ] **Foreign keys defined** (cascading deletes configured)
- [ ] **Connection pool sized** (20 connections, 30s timeout)
- [ ] **Migrations tested** (upgrade and downgrade)
- [ ] **Backup configured** (daily, 30-day retention)
- [ ] **Point-in-time recovery enabled** (for production)
- [ ] **Query optimization verified** (no N+1 queries)
- [ ] **Database tier adequate** (db-custom-2-7680 for production)

### Monitoring

- [ ] **Prometheus metrics exposed** (/metrics endpoint)
- [ ] **Error rate alerts** (>5% triggers alert)
- [ ] **Latency alerts** (P95 >2s triggers alert)
- [ ] **AI cost tracking** (daily spend monitored)
- [ ] **Budget alerts configured** (50%, 80%, 100% thresholds)
- [ ] **Structured logging** (JSON format with context)
- [ ] **Request tracing** (correlation IDs)
- [ ] **Health check endpoints** (/health, /health/ready, /health/live)
- [ ] **Database connection monitoring** (pool usage)
- [ ] **Cache hit rate tracking** (Redis operations)

### Performance

- [ ] **Redis caching operational** (1hr TTL for tokens, 24hr for extractions)
- [ ] **Redis HA enabled** (STANDARD_HA tier for production)
- [ ] **AI response caching** (by image hash)
- [ ] **Image preprocessing optimized** (CV pipeline)
- [ ] **Batch processing semaphore** (limit: 5 concurrent)
- [ ] **Frontend bundle optimized** (<300KB gzipped)
- [ ] **List virtualization implemented** (for 100+ tokens)
- [ ] **React memoization applied** (TokenCard, visualizers)
- [ ] **Load testing passed** (10 req/s sustained)
- [ ] **P95 latency acceptable** (<2s for extraction)

### Documentation

- [ ] **API documentation complete** (OpenAPI/Swagger)
- [ ] **Architecture diagrams updated** (component interactions)
- [ ] **Deployment runbook created** (step-by-step procedures)
- [ ] **Troubleshooting guide written** (common issues)
- [ ] **Environment setup documented** (local, staging, production)
- [ ] **Configuration reference complete** (all env vars)
- [ ] **Code comments adequate** (complex logic explained)
- [ ] **CHANGELOG maintained** (version history)

### CI/CD

- [ ] **Build pipeline working** (Docker image builds)
- [ ] **Test suite passing** (unit, integration, E2E)
- [ ] **Security scans enforced** (blocking, not warning)
- [ ] **Test coverage adequate** (>80% overall)
- [ ] **Staging deployment automated** (on merge to develop)
- [ ] **Production deployment gated** (manual approval)
- [ ] **Automated rollback configured** (on smoke test failure)
- [ ] **CI time optimized** (<10 minutes)
- [ ] **Artifact caching working** (pip, npm, Docker layers)

### Rollback Procedures

- [ ] **Previous revision retained** (Cloud Run revisions)
- [ ] **Database rollback tested** (alembic downgrade)
- [ ] **Feature flags available** (for gradual rollout)
- [ ] **Rollback runbook documented** (step-by-step)
- [ ] **Monitoring during rollback** (verify recovery)

### Disaster Recovery

- [ ] **Database backups verified** (test restore)
- [ ] **Multi-region strategy defined** (if required)
- [ ] **RTO/RPO documented** (recovery time/point objectives)
- [ ] **DR runbook created** (disaster scenarios)
- [ ] **Communication plan** (incident notification)

---

## 9. Gap Analysis

### Missing Deployment Configurations

| Gap | Impact | Recommended Action |
|-----|--------|-------------------|
| **No Terraform for Redis** | Manual setup required | Add `redis.tf` to deploy/terraform |
| **No Cloud Run YAML** | Deployment config unclear | Create `cloud-run-service.yaml` template |
| **Missing GCP IAM roles** | Permission issues | Document required roles in deployment guide |
| **No staging/prod parity** | Environment drift | Create environment-specific Terraform workspaces |

### Missing Monitoring Setup

| Gap | Impact | Recommended Action |
|-----|--------|-------------------|
| **No custom metrics** | Limited observability | Add application-specific Prometheus metrics |
| **No distributed tracing** | Debugging difficult | Integrate OpenTelemetry or Cloud Trace |
| **No log aggregation** | Logs scattered | Configure Cloud Logging with log-based metrics |
| **No SLO definitions** | No reliability targets | Define SLOs for availability and latency |
| **No alert runbooks** | Slow incident response | Create runbook for each alert |

### Missing CI/CD Integration

| Gap | Impact | Recommended Action |
|-----|--------|-------------------|
| **No E2E tests in CI** | Regressions slip through | Add Playwright tests to CI pipeline |
| **No performance tests in CI** | Performance regressions | Add load tests to staging deployment |
| **No database migration check** | Failed migrations | Add migration dry-run to CI |
| **No dependency update automation** | Security vulnerabilities | Configure Dependabot or Renovate |
| **No preview environments** | PR review difficult | Add Cloud Run preview deployments |

### Missing Load Testing Plans

| Gap | Impact | Recommended Action |
|-----|--------|-------------------|
| **No load test scripts** | Performance unknown | Create k6 or Locust test scripts |
| **No performance baseline** | No regression detection | Establish baseline metrics |
| **No cost projections** | Budget surprises | Model AI costs at different scales |
| **No capacity planning** | Scaling issues | Document scaling thresholds |

### Missing Features from Planning Docs

| Feature | Documented In | Status | Gap |
|---------|--------------|--------|-----|
| Typography Token | TOKEN_FACTORY_PLANNING | Planned | No implementation timeline |
| Shadow Token | TOKEN_FACTORY_PLANNING | Mentioned | No planning document |
| Multi-tenant isolation | Backend Roadmap | Partial | No data isolation strategy |
| Webhook notifications | Not documented | Missing | No event notification system |
| Token versioning | Not documented | Missing | No history/audit trail for tokens |

---

## 10. Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **AI API rate limits** | Medium | High | Implement request queuing, cache aggressively |
| **AI API cost overruns** | High | Medium | Set hard daily limits, alert at 80% |
| **Database performance degradation** | Low | High | Index optimization, connection pooling, read replicas |
| **Redis memory exhaustion** | Medium | Medium | Set maxmemory policy, monitor usage |
| **CV pipeline memory leaks** | Low | Medium | Explicit cleanup, memory monitoring |
| **Frontend bundle bloat** | Medium | Low | Bundle analysis, tree shaking, lazy loading |
| **SSE connection limits** | Low | Medium | Connection pooling, timeouts |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Failed deployment** | Medium | High | Automated rollback, smoke tests |
| **Database migration failure** | Low | Critical | Migration dry-run, backup before migrate |
| **Secret rotation issues** | Low | High | Document rotation procedure, test regularly |
| **Cloud Run cold starts** | High | Low | Min instances = 1, optimize startup |
| **Redis failover during operation** | Low | Medium | Redis HA, connection retry logic |
| **Log loss during incidents** | Medium | Medium | Real-time log export, alerting |

### Security Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **JWT secret compromise** | Low | Critical | Secret rotation, short expiry |
| **API key leak** | Medium | High | Key rotation, scope restrictions |
| **SQL injection** | Low | Critical | SQLAlchemy ORM, input validation |
| **SSRF exploitation** | Medium | High | URL validation, private IP blocking |
| **Dependency vulnerabilities** | High | Medium | Automated scanning, regular updates |
| **Unauthorized data access** | Low | High | Ownership checks, audit logging |

### Mitigation Priorities

1. **Immediate (Week 1):**
   - Enable security scans blocking
   - Configure budget alerts
   - Implement rate limiting

2. **Short-term (Week 2-3):**
   - Deploy authentication system
   - Set up AI cost tracking
   - Configure Redis HA

3. **Medium-term (Week 4-6):**
   - Complete audit logging
   - Implement automated rollback
   - Add distributed tracing

4. **Ongoing:**
   - Regular security reviews
   - Dependency updates
   - Performance monitoring

---

## 11. Appendix: Quick Reference

### Key File Locations Across Branches

#### Current Branch (Spacing Token Pipeline)
```
docs/planning/token-pipeline-planning/
├── SPACING_TOKEN_PIPELINE_PLANNING.md    # Spacing token implementation
├── TOKEN_FACTORY_PLANNING.md             # Factory abstraction
└── CROSS_REFERENCE_AND_PRODUCTION_READINESS.md  # This document

src/copy_that/
├── tokens/
│   ├── factory/                          # Token factory core (to create)
│   └── spacing/                          # Spacing implementation (to create)
├── interfaces/api/spacing.py             # API router (to create)
└── domain/models.py                      # Add SpacingToken model
```

#### Backend Optimization Branch
```
docs/backend-analysis/
├── 01-codebase-overview.md
├── 02-database-improvements.md
├── 03-security-hardening.md
└── 04-implementation-roadmap.md          # Referenced in this doc

src/copy_that/
├── infrastructure/
│   ├── security/                         # Auth, rate limiting
│   └── cache/                            # Redis caching
└── domain/models.py                      # User, APIKey, APIUsageLog
```

#### CV Preprocessing Branch
```
docs/cv-preprocessing-pipeline/
├── 01-architecture-overview.md
├── 02-data-structures.md
├── 03-validation-rules.md
├── 04-preprocessing-ops.md
├── 05-concurrency-patterns.md
├── 06-unit-testing-strategy.md
└── 07-implementation-roadmap.md          # Referenced in this doc

src/copy_that/
├── infrastructure/cv/
│   ├── loader.py                         # Async loading
│   ├── validator.py                      # Image validation
│   ├── preprocessor.py                   # OpenCV operations
│   ├── optimizer.py                      # Compression
│   └── preprocessing.py                  # Pipeline orchestrator
└── application/services/image_service.py # Application integration
```

#### Frontend Infrastructure Branch
```
docs/frontend-infrastructure-analysis/
├── 01-executive-summary.md
├── 02-codebase-analysis.md
├── 03-infrastructure-analysis.md
├── 04-recommendations.md
└── 05-implementation-roadmap.md          # Referenced in this doc

frontend/
├── src/
│   ├── store/                            # Zustand stores
│   ├── components/                       # React components
│   └── config/tokenTypeRegistry.tsx      # Token type config
└── vite.config.ts                        # Build configuration
```

### Important Configuration Values

```python
# Application Defaults
MAX_CONCURRENT_EXTRACTIONS = 5
MAX_SPACING_TOKENS = 12
DEDUPLICATION_THRESHOLD = 0.10  # 10%
REDIS_CACHE_TTL = 3600  # 1 hour
EXTRACTION_CACHE_TTL = 86400  # 24 hours

# Database
POOL_SIZE = 20
MAX_OVERFLOW = 20
POOL_RECYCLE = 1800
POOL_TIMEOUT = 30

# Rate Limiting
REQUESTS_PER_MINUTE = 60
REQUESTS_PER_HOUR = 1000

# Authentication
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_ALGORITHM = "HS256"

# AI API
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
CLAUDE_MAX_TOKENS = 2048
CLAUDE_INPUT_COST = 0.003  # per 1k tokens
CLAUDE_OUTPUT_COST = 0.015  # per 1k tokens

# Cloud Run
CONTAINER_MEMORY = "2Gi"
CONTAINER_CPU = "2"
TIMEOUT_SECONDS = 300
MAX_INSTANCES = 10
CONCURRENCY = 80
```

### Critical Code Patterns

#### Token Factory Pattern (Extend for new tokens)
```python
# 1. Define token model extending BaseToken
class SpacingToken(BaseToken):
    token_type = "spacing"
    # ... fields

# 2. Define extractor extending BaseExtractor
class SpacingExtractor(BaseExtractor[SpacingToken]):
    token_class = SpacingToken
    # ... implement _build_extraction_prompt, _parse_ai_response

# 3. Define aggregator extending BaseAggregator
class SpacingAggregator(BaseAggregator[SpacingToken]):
    # ... implement _calculate_similarity, _sort_tokens, _generate_statistics

# 4. Register plugin
register_token_plugin('spacing', SpacingToken, SpacingExtractor, SpacingAggregator, generators)
```

#### Cache-Through Pattern
```python
async def get_with_cache(key, fetch_func, cache, ttl=3600):
    cached = await cache.get(key)
    if cached:
        return cached

    data = await fetch_func()
    await cache.set(key, data, ttl)
    return data
```

#### Graceful Degradation Pattern
```python
async def process_with_fallback(source):
    strategies = [full_preprocess, reduced_preprocess, minimal_preprocess, passthrough]

    for strategy in strategies:
        try:
            return await strategy(source)
        except Exception as e:
            logger.warning(f"Strategy {strategy.__name__} failed: {e}")
            continue

    raise ProcessingError("All strategies failed")
```

#### Rate Limiting Pattern
```python
async def rate_limit_middleware(request, call_next, redis):
    key = f"ratelimit:{request.user.id}:{get_minute()}"

    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 60)
    count, _ = await pipe.execute()

    if count > LIMIT:
        raise HTTPException(429, "Rate limit exceeded")

    return await call_next(request)
```

---

**Version:** 1.0 | **Last Updated:** 2025-11-22 | **Status:** Planning Document

---

## Document Metadata

| Field | Value |
|-------|-------|
| Created | 2025-11-22 |
| Author | Claude Code Agent |
| Dependencies | All 4 branch planning documents |
| Next Steps | Review with team, prioritize gaps, begin Phase 1 |
