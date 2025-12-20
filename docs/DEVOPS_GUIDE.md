# DevOps Guide - Copy That Platform

**Solo Developer Workflow** | **Last Updated:** 2025-12-08

---

## 🎯 Quick Start

```bash
# Local development (hot reload)
docker-compose up api postgres redis

# Test production build locally
./scripts/test-production-build.sh

# Deploy to production
git push origin main  # Automatic CI/CD via GitHub Actions
```

---

## 📋 Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Usage Patterns](#docker-usage-patterns)
3. [Testing Production Builds](#testing-production-builds)
4. [Deployment Workflow](#deployment-workflow)
5. [Secret Management](#secret-management)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Troubleshooting](#troubleshooting)

---

## 1. Local Development Setup

### Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- Git
- (Optional) Node.js 20+ for frontend development
- (Optional) Python 3.12+ for backend development without Docker

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/joshband/copy-that.git
cd copy-that

# 2. Create .env file
cp .env.example .env

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose run --rm api alembic upgrade head

# 5. Verify health
curl http://localhost:8000/health
```

### .env Configuration

```bash
# Required for local development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/copy_that_dev
SECRET_KEY=your-local-secret-key
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional
LOG_LEVEL=DEBUG
ENVIRONMENT=local
```

---

## 2. Docker Usage Patterns

### Development Workflow (Hot Reload)

```bash
# Start development services
docker-compose up api postgres redis

# Or run in background
docker-compose up -d api postgres redis

# Watch logs
docker-compose logs -f api

# Stop services
docker-compose down
```

**What's included:**
- ✅ Hot reload on code changes
- ✅ Source code mounted as volume
- ✅ Debug logging enabled
- ✅ Port 8000 exposed

### Production Testing (Exact Cloud Run Build)

```bash
# Build and test production image
./scripts/test-production-build.sh

# Or manually:
docker-compose --profile prod-test up api-prod-test

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/status

# Cleanup
docker-compose --profile prod-test down
```

**What's different from dev:**
- ✅ Multi-stage optimized build
- ✅ Non-root user (appuser)
- ✅ Production dependencies only
- ✅ Gunicorn with uvicorn workers
- ✅ Port 8080 (matches Cloud Run)

### Frontend Development

```bash
# Start frontend + backend
docker-compose up frontend api postgres

# Or use local Vite dev server
pnpm dev  # Faster hot reload

# Production frontend build
docker-compose up frontend
```

---

## 3. Testing Production Builds

### Automated Testing Script

```bash
./scripts/test-production-build.sh
```

**What it does:**
1. ✅ Builds production Docker image
2. ✅ Checks image size
3. ✅ Starts production-like environment
4. ✅ Runs health checks (retries 10x)
5. ✅ Tests API endpoints
6. ✅ Shows logs
7. ✅ Provides cleanup commands

### Manual Testing

```bash
# Build production image
docker build -f Dockerfile --target production -t copy-that:prod .

# Run standalone
docker run -p 8080:8080 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e SECRET_KEY="..." \
  copy-that:prod

# Test with docker-compose
docker-compose --profile prod-test up

# Inspect running container
docker exec -it copy-that-api-prod-test /bin/sh

# Check processes
docker exec copy-that-api-prod-test ps aux

# View logs
docker logs copy-that-api-prod-test --tail 50 -f
```

---

## 4. Deployment Workflow

### Architecture Overview

```
Local Development → GitHub Push → GitHub Actions → Cloud Run
       ↓                ↓                ↓              ↓
  Docker Dev     Build & Push     Workload Identity   Production
    (port 8000)    to Artifact      (OAuth)            (port 8080)
                   Registry
```

### Deployment Flow

```bash
# 1. Test locally first
./scripts/test-production-build.sh

# 2. Commit changes
git add .
git commit -m "feat: your feature"

# 3. Push to trigger deployment
git push origin main  # Deploys to production
git push origin develop  # Deploys to staging

# 4. Monitor deployment
# GitHub Actions → copy-that → Actions tab
```

### What Happens Automatically

**On Push to `main`:**
1. ✅ Security scan (pip-audit, bandit, gitleaks)
2. ✅ Lint & type check (ruff, mypy)
3. ✅ Test suite (pytest with PostgreSQL/Redis)
4. ✅ Docker build (multi-stage production)
5. ✅ Push to Artifact Registry
6. ✅ Deploy to Cloud Run (production)
7. ✅ Run database migrations
8. ✅ Smoke tests (health + status)
9. ✅ Notifications (success/failure)

**On Push to `develop`:**
- Same flow but deploys to staging environment

### Manual Deployment

```bash
# Trigger manual deployment
gh workflow run deploy.yml -f environment=production

# Or via GitHub UI:
# Actions → Deploy to Cloud Run → Run workflow
```

---

## 5. Secret Management

### GitHub Secrets (Required)

Set these in: **GitHub → Settings → Secrets and variables → Actions**

| Secret Name | Description | Example |
|------------|-------------|---------|
| `NEON_DATABASE_URL` | Neon PostgreSQL connection | `postgresql+asyncpg://user:pass@host/db` |
| `APP_SECRET_KEY` | FastAPI secret key | `openssl rand -hex 32` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-...` |
| `GCP_PROJECT_ID` | GCP project ID | `copy-that-platform` |

### Getting Neon Connection String

```bash
# Via Neon CLI
neonctl connection-string

# Or from Neon dashboard:
# Projects → copy-that → Connection Details → Connection string
```

**Convert for asyncpg:**
```bash
# Neon gives you:
postgresql://user:pass@host/db

# Convert to asyncpg format:
postgresql+asyncpg://user:pass@host/db?sslmode=require
```

### Local .env File

```bash
# .env (local development only - never commit!)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/copy_that_dev
SECRET_KEY=local-dev-secret-key-not-for-production
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
LOG_LEVEL=DEBUG
ENVIRONMENT=local
```

---

## 6. CI/CD Pipeline

### GitHub Actions Workflows

| Workflow | Trigger | Purpose | Duration |
|----------|---------|---------|----------|
| `ci.yml` | Push to main/develop | Tests & validation | ~5-8 min |
| `build.yml` | Push to main/develop | Docker build & push | ~3-5 min |
| `deploy.yml` | After build.yml | Deploy to Cloud Run | ~2-3 min |
| _Removed: `neon_workflow.yml`_ | — | — | Removed (preview DBs unused) |

### Pipeline Optimizations (Applied)

✅ **Job Dependencies:**
- Lint runs first (fastest feedback)
- Tests only run if lint passes
- Docker only builds if tests pass
- Saves ~5-10 minutes on lint failures

✅ **Caching:**
- Python dependencies cached (2-3x faster)
- Docker layers cached (GitHub Actions cache)
- uv cache enabled

✅ **Timeouts:**
- Security: 10 minutes
- Lint: 10 minutes
- Tests: 20 minutes
- Docker: 15 minutes

✅ **Workload Identity:**
- Short-lived OAuth tokens (1 hour)
- No long-lived service account keys
- Better security and audit trail

### Monitoring Deployments

```bash
# View workflow runs
gh run list --workflow=deploy.yml

# Watch specific run
gh run watch

# View logs
gh run view --log

# Or check GitHub UI:
# https://github.com/joshband/copy-that/actions
```

---

## 7. Troubleshooting

### Common Issues

#### 🔴 "Failed to build Docker image"

```bash
# Check build locally
docker build -f Dockerfile --target production -t copy-that:test .

# Check for missing dependencies
grep -r "import" src/ | cut -d: -f2 | sort | uniq

# Verify requirements.txt vs pyproject.toml
```

#### 🔴 "Health check failed"

```bash
# Check container logs
docker-compose logs api

# Inspect health endpoint
curl -v http://localhost:8000/health

# Check database connection
docker-compose exec api python -c "from copy_that.infrastructure.database import engine; print(engine)"
```

#### 🔴 "Database migration failed"

```bash
# Check migration status locally
docker-compose run --rm api alembic current

# View migration history
docker-compose run --rm api alembic history

# Manually run migrations
docker-compose run --rm api alembic upgrade head
```

#### 🔴 "Workload Identity authentication failed"

Verify in Terraform:
```bash
cd deploy/terraform
terraform output workload_identity_provider

# Should match:
# projects/296606576830/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider
```

#### 🔴 "Cloud Run deployment timeout"

```bash
# Check deployment status
gcloud run services describe copy-that-api-production --region us-central1

# View Cloud Run logs
gcloud run services logs read copy-that-api-production --region us-central1 --limit 50
```

### Debugging Commands

```bash
# Check running containers
docker-compose ps

# Shell into API container
docker-compose exec api /bin/bash

# Restart specific service
docker-compose restart api

# Rebuild and restart
docker-compose up --build api

# View all logs
docker-compose logs

# Check resource usage
docker stats
```

### Performance Profiling

```bash
# Check image layer sizes
docker history copy-that:prod-test

# Analyze build time
docker build --progress=plain -f Dockerfile --target production -t copy-that:test . 2>&1 | tee build.log

# Check for cached layers
# Look for "CACHED" in build output
```

---

## 📊 Cost Optimization Summary

| Service | Status | Monthly Cost |
|---------|--------|--------------|
| **Neon Database** | ✅ Active | $0 (free tier) |
| **Cloud Run** | ✅ Optimized | $0-5 (scale to zero) |
| **Artifact Registry** | ✅ Active | $0-2 (storage) |
| **VPC/Networking** | ✅ Active | $5-10 (NAT, connectors) |
| **Cloud SQL** | ❌ Removed | Saved $25-50/month |
| **Redis** | ❌ Removed | Saved $30-40/month |
| **TOTAL** | | **~$5-17/month** |

**Previous cost (with Cloud SQL):** ~$60-100/month
**Current cost (Neon only):** ~$5-17/month
**Savings:** **~$55-90/month (80-90% reduction)**

---

## 🚀 Deployment Checklist

Before deploying:

- [ ] Run `pnpm typecheck` (must pass)
- [ ] Run `./scripts/test-production-build.sh` (must pass)
- [ ] Verify GitHub secrets are set
- [ ] Check Neon database is accessible
- [ ] Review recent commits
- [ ] Monitor first deployment in GitHub Actions

After deploying:

- [ ] Verify health check passes
- [ ] Test key API endpoints
- [ ] Check Cloud Run logs for errors
- [ ] Monitor performance for 10-15 minutes
- [ ] Verify database migrations applied

---

## 📚 Additional Resources

- **Neon Docs:** https://neon.tech/docs
- **Cloud Run Docs:** https://cloud.google.com/run/docs
- **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/
- **GitHub Actions:** https://docs.github.com/en/actions

---

## 🆘 Getting Help

**Check these first:**
1. GitHub Actions logs (most detailed)
2. Cloud Run logs (`gcloud run services logs read ...`)
3. Neon dashboard (database metrics)
4. This guide's troubleshooting section

**Still stuck?**
- Check recent commits for breaking changes
- Review `.github/workflows/` for workflow changes
- Verify environment variables match across local/prod

---

## 🔄 Common Workflows

### Adding a New Feature

```bash
# 1. Develop locally
docker-compose up api

# 2. Add tests
pytest tests/unit/test_new_feature.py

# 3. Test production build
./scripts/test-production-build.sh

# 4. Commit and push
git add .
git commit -m "feat: new feature"
git push origin main
```

### Database Schema Changes

```bash
# 1. Create migration
docker-compose run --rm api alembic revision --autogenerate -m "add new table"

# 2. Apply locally
docker-compose run --rm api alembic upgrade head

# 3. Test migration
docker-compose run --rm api pytest tests/

# 4. Deploy (migrations run automatically in CD pipeline)
git push origin main
```

### Updating Dependencies

```bash
# 1. Update pyproject.toml
# Add new dependency

# 2. Rebuild image
docker-compose build api

# 3. Test
docker-compose up api

# 4. Update requirements.txt (if needed)
# 5. Deploy
git push origin main
```

---

## 🎯 Performance Tips

### Faster Docker Builds

1. **Use .dockerignore** ✅ (already configured)
2. **Leverage layer caching** ✅ (dependencies before source)
3. **Use BuildKit:** `DOCKER_BUILDKIT=1 docker build ...`
4. **Multi-stage builds** ✅ (70% smaller images)

### Faster CI Runs

1. **Python caching** ✅ (2-3x faster)
2. **Job dependencies** ✅ (fail fast)
3. **Parallel jobs** ✅ (security, lint, tests run in parallel)
4. **Skip unnecessary jobs:** Use `[skip ci]` in commit message

### Reducing Costs

1. **Scale to zero** ✅ (Cloud Run min-instances=0)
2. **Use Neon free tier** ✅ (avoid Cloud SQL)
3. **Optimize image size** ✅ (multi-stage builds)
4. **Monitor usage:** Cost dashboard (coming soon)

---

## 📈 Metrics to Monitor

### Application Health
- Cloud Run request latency
- Error rates (5xx responses)
- Container startup time
- Memory usage

### Database (Neon)
- Connection count
- Query performance
- Storage size
- Active time (affects billing)

### CI/CD
- Build duration
- Test pass rate
- Deployment frequency
- Failed deployment rate

### Cost
- Cloud Run compute time
- Artifact Registry storage
- Network egress
- Neon compute time

---

## 🔐 Security Best Practices

### ✅ Already Implemented

- Workload Identity Federation (no long-lived keys)
- Non-root Docker user
- Secret Manager / GitHub Secrets (not hardcoded)
- Security scanning (pip-audit, bandit, gitleaks)
- HTTPS only (Cloud Run default)
- Private networking for VPC

### 🎯 Recommended Next Steps

- [ ] Enable Cloud Armor (DDoS protection)
- [ ] Add rate limiting
- [ ] Implement request signing
- [ ] Set up log-based alerting
- [ ] Enable audit logging

---

## 🚀 Advanced Usage

### Testing Different Environments

```bash
# Staging environment
docker-compose -f docker-compose.staging.yml up

# Production testing
docker-compose --profile prod-test up

# Integration testing
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Database Backups

```bash
# Neon handles backups automatically ✅
# Point-in-time recovery: 7 days

# Manual backup (if needed)
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

### Viewing Metrics

```bash
# Cloud Run metrics
gcloud run services describe copy-that-api-production --region us-central1

# Real-time logs
gcloud run services logs tail copy-that-api-production --region us-central1

# Neon metrics
# Use Neon dashboard or MCP tools
```

---

## 🎓 Learning Resources

### Docker
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

### CI/CD
- [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart)
- [Workload Identity](https://cloud.google.com/iam/docs/workload-identity-federation)

### Cloud Run
- [Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)
- [Best Practices](https://cloud.google.com/run/docs/tips/general)

---

**Last Updated:** 2025-12-08
**Maintained By:** Solo Developer (Josh)
