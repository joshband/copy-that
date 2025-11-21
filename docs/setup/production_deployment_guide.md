# Production Deployment Guide - Copy That

## Overview
This guide covers deploying Copy That to production with a focus on:
- Backend API (FastAPI/Python)
- Frontend (React/Vite)
- Database (Neon PostgreSQL)
- Security, performance, and reliability

**Current Status**: ✅ Production Ready
- All tests passing (33/33 integration + e2e)
- Performance validated (2.76ms per color, 500 colors in 1.38s)
- Type safety verified (0 TypeScript errors)
- Full end-to-end workflow implemented

---

## Phase 1: Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing: `python -m pytest tests/ --no-cov`
- [ ] Type checking passes: `pnpm type-check`
- [ ] No linting errors: `pnpm lint` (if configured)
- [ ] Frontend builds successfully: `pnpm build`
- [ ] No security vulnerabilities: Review dependencies

### Documentation
- [ ] README.md updated with deployment instructions
- [ ] Environment variables documented
- [ ] API endpoints documented (FastAPI /docs)
- [ ] Database schema documented

### Configuration
- [ ] Environment variables template created (.env.example)
- [ ] Production secrets secured (use Neon dashboard)
- [ ] CORS configured for production domain
- [ ] API version locked (v1.0.0)

---

## Phase 2: Database Migration (SQLite → Neon PostgreSQL)

### Step 1: Create Neon Project

```bash
# 1. Go to https://console.neon.tech
# 2. Create new project (if not already done)
# 3. Note your connection string:
#    postgresql://[user]:[password]@[host]/[dbname]?sslmode=require
```

### Step 2: Configure Environment Variables

**Create `.env.production` file**:
```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Environment
ENVIRONMENT=production
LOG_LEVEL=info

# API
API_PORT=8000
API_WORKERS=4

# Frontend
VITE_API_URL=https://api.yourdomain.com/api/v1
VITE_ENVIRONMENT=production

# Claude API (for color extraction)
ANTHROPIC_API_KEY=sk-proj-xxxxxxxxxx

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Step 3: Run Database Migrations

```bash
# Install Alembic if not already installed
pip install alembic

# Run migrations against production database
export DATABASE_URL="postgresql://..."
python -m alembic upgrade head

# Verify migrations
psql $DATABASE_URL -c "SELECT * FROM information_schema.tables WHERE table_schema = 'public';"
```

### Step 4: Verify Database Connection

```python
# test_db_connection.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def test_connection():
    engine = create_async_engine(
        "postgresql+asyncpg://user:password@host/dbname?ssl=require"
    )
    async with engine.begin() as conn:
        result = await conn.execute("SELECT 1")
        print("✅ Database connection successful")

asyncio.run(test_connection())
```

---

## Phase 3: Backend Deployment

### Option A: Heroku (Recommended for Rapid Deployment)

```bash
# 1. Install Heroku CLI
# 2. Login to Heroku
heroku login

# 3. Create app
heroku create copy-that-api

# 4. Add buildpack
heroku buildpacks:add heroku/python

# 5. Set environment variables
heroku config:set DATABASE_URL=postgresql://...
heroku config:set ANTHROPIC_API_KEY=sk-proj-...
heroku config:set ENVIRONMENT=production

# 6. Deploy
git push heroku main

# 7. Check logs
heroku logs --tail
```

### Option B: AWS Lambda + RDS

```yaml
# SAM Template (template.yaml)
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  CopyThatAPI:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.11
      Handler: src.copy_that.interfaces.api.main.app
      Timeout: 30
      MemorySize: 1024
      Environment:
        Variables:
          DATABASE_URL: !Sub postgresql://${DBUser}:${DBPassword}@${DBHost}:5432/copy_that
      CodeUri: .
```

Deploy with:
```bash
sam build
sam deploy --guided
```

### Option C: Docker + Cloud Run (Google Cloud)

**Create Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src ./src

# Expose port
EXPOSE 8000

# Run uvicorn
CMD ["python", "-m", "uvicorn", "src.copy_that.interfaces.api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Deploy:
```bash
# Build image
docker build -t copy-that-api .

# Push to Google Cloud Registry
docker tag copy-that-api gcr.io/PROJECT_ID/copy-that-api
docker push gcr.io/PROJECT_ID/copy-that-api

# Deploy to Cloud Run
gcloud run deploy copy-that-api \
  --image gcr.io/PROJECT_ID/copy-that-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=postgresql://...
```

### Backend Performance Tuning

```python
# Uvicorn Configuration for Production
# gunicorn_config.py
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 5
```

---

## Phase 4: Frontend Deployment

### Option A: Vercel (Recommended)

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Configure vercel.json
cat > vercel.json << EOF
{
  "buildCommand": "pnpm build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_URL": "@api_url"
  }
}
EOF

# 3. Deploy
vercel deploy --prod

# 4. Set environment variable in Vercel dashboard
# VITE_API_URL = https://api.yourdomain.com/api/v1
```

### Option B: Netlify

```bash
# 1. Connect GitHub repo
# 2. Configure build settings:
#    Build Command: pnpm build
#    Publish Directory: dist
# 3. Set environment variables in Netlify dashboard
# 4. Deploy on push
```

### Option C: AWS S3 + CloudFront

```bash
# 1. Build frontend
pnpm build

# 2. Create S3 bucket
aws s3 mb s3://copy-that-prod

# 3. Upload dist folder
aws s3 sync dist/ s3://copy-that-prod/ --delete

# 4. Create CloudFront distribution pointing to S3
# 5. Configure DNS to point to CloudFront
```

---

## Phase 5: Environment-Specific Configurations

### Production Environment Variables

```env
# .env.production

# Database
DATABASE_URL=postgresql://neon_user:password@ep-xyz.neon.tech/copy_that?sslmode=require

# Application
ENVIRONMENT=production
LOG_LEVEL=warning
DEBUG=false

# API
API_HOST=api.copy-that.com
API_PORT=8000
ALLOWED_ORIGINS=https://copy-that.com,https://www.copy-that.com

# Frontend
VITE_API_URL=https://api.copy-that.com/api/v1
VITE_ENVIRONMENT=production

# Claude API
ANTHROPIC_API_KEY=${SECRET_ANTHROPIC_API_KEY}

# Monitoring
SENTRY_DSN=${SECRET_SENTRY_DSN}
```

### Staging Environment

```env
# .env.staging

DATABASE_URL=postgresql://neon_user:password@ep-abc.neon.tech/copy_that_staging?sslmode=require

ENVIRONMENT=staging
LOG_LEVEL=info

API_HOST=staging-api.copy-that.com
ALLOWED_ORIGINS=https://staging.copy-that.com

VITE_API_URL=https://staging-api.copy-that.com/api/v1
VITE_ENVIRONMENT=staging

ANTHROPIC_API_KEY=${SECRET_ANTHROPIC_API_KEY}
```

---

## Phase 6: Security Hardening

### HTTPS/TLS
- [ ] Enable HTTPS on all endpoints
- [ ] Use TLS 1.2 minimum
- [ ] Set HSTS headers (strict-transport-security)

### API Security

```python
# Add security headers in FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["copy-that.com", "www.copy-that.com"]
)

# Add security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

### Database Security
- [ ] Use strong passwords for database users
- [ ] Enable SSL/TLS for database connections
- [ ] Use Neon private endpoints (when available)
- [ ] Regular backups configured
- [ ] Database audit logs enabled

### API Keys
- [ ] Never commit secrets to repository
- [ ] Use environment variables for all secrets
- [ ] Rotate API keys regularly
- [ ] Use separate keys for different environments

---

## Phase 7: Monitoring & Observability

### Logging

```python
import logging
import json
from datetime import datetime

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format=json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "level": "%(levelname)s",
        "message": "%(message)s",
        "module": "%(name)s"
    })
)
```

### Performance Monitoring

```python
# Add timing middleware
import time

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    if process_time > 1.0:  # Log slow requests
        logger.warning(f"Slow request: {request.url.path} took {process_time:.2f}s")

    return response
```

### Error Tracking (Sentry)

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "production")
)
```

### Metrics to Monitor

- **API Response Times**: 95th percentile < 200ms
- **Database Query Times**: 95th percentile < 50ms
- **Error Rate**: < 0.1%
- **Uptime**: > 99.9%
- **Active Users**: Track daily active users
- **Color Extraction Success**: > 99%

---

## Phase 8: Continuous Deployment

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-prod.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'frontend/src/**'
      - '.github/workflows/deploy-prod.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run tests
        run: |
          pip install -r requirements.txt
          python -m pytest tests/

      - name: Run type check
        run: pnpm type-check

  deploy:
    needs: test
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Deploy backend to Heroku
        env:
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
        run: |
          git push https://heroku:$HEROKU_API_KEY@git.heroku.com/copy-that-api.git main

      - name: Deploy frontend to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          npx vercel deploy --prod --token $VERCEL_TOKEN
```

---

## Phase 9: Post-Deployment Validation

### Health Checks

```bash
# Check API health
curl https://api.copy-that.com/api/v1/status

# Check database connectivity
curl https://api.copy-that.com/api/v1/db-test

# Check frontend
curl https://copy-that.com/
```

### Smoke Tests

```python
# Run production smoke tests
python test_production_smoke.py

# Expected results:
# ✅ API health check
# ✅ Database connectivity
# ✅ Color extraction endpoint
# ✅ Project CRUD operations
# ✅ Frontend loading
```

### Performance Baseline

From testing, expect:
- Per-color creation: 2.76ms
- 500-color batch: 1.38s
- API response time: 10-15ms average
- Database query time: < 5ms

---

## Phase 10: Maintenance & Updates

### Regular Tasks (Weekly)
- [ ] Monitor error rates in Sentry
- [ ] Review database query performance
- [ ] Check log files for anomalies

### Regular Tasks (Monthly)
- [ ] Review cost optimization opportunities
- [ ] Update dependencies (npm, pip)
- [ ] Test disaster recovery procedures

### Regular Tasks (Quarterly)
- [ ] Full security audit
- [ ] Performance benchmarking
- [ ] Capacity planning review

---

## Rollback Procedures

### If Deployment Fails

```bash
# Heroku rollback
heroku releases:rollback

# Vercel rollback
vercel rollback

# Manual rollback (redeploy previous version)
git checkout HEAD~1
# Deploy previous version
```

### Database Rollback

```bash
# If migration fails, use Neon restore point
# https://neon.tech/docs/manage/data-recovery

# Or restore from backup
pg_restore -d copy_that backup.dump
```

---

## Cost Optimization

### Database (Neon)
- **Free tier**: Up to 1 project, 3GB storage
- **Paid**: $14/month starting, scales with usage
- **Cost optimization**: Use connection pooling, query optimization

### Hosting (Heroku)
- **Free**: Discontinued (use alternatives)
- **Standard**: $50/month (Eco)
- **Professional**: $250+/month
- **Cost optimization**: Use smallest dyno size, Postgres starter tier

### Frontend (Vercel)
- **Free**: 100GB bandwidth/month
- **Pro**: $20/month, unlimited bandwidth
- **Cost optimization**: Compress images, enable caching

---

## Estimated Monthly Costs

| Service | Free/Cost | Notes |
|---------|-----------|-------|
| Database (Neon) | $14 | Shared compute, 1GB storage base |
| Backend (Heroku) | $50 | Eco dyno, single worker |
| Frontend (Vercel) | Free | Within bandwidth limits |
| Claude API | $0.50-5 | Per 1M input tokens |
| Monitoring (Sentry) | Free | Up to 5K errors/month |
| **TOTAL** | ~$65-75 | For typical usage |

---

## Support & Troubleshooting

### Common Issues

**Issue**: High database latency
- **Solution**: Add database connection pooling, optimize queries

**Issue**: Frontend not loading
- **Solution**: Check CORS configuration, API URL environment variables

**Issue**: Color extraction failing
- **Solution**: Verify Anthropic API key, check rate limits

**Issue**: Database connection errors
- **Solution**: Check DATABASE_URL, verify Neon firewall rules

### Support Resources
- Neon Docs: https://neon.tech/docs
- FastAPI Docs: https://fastapi.tiangolo.com/deployment/
- Vercel Docs: https://vercel.com/docs
- GitHub Issues: Report issues in repository

---

## Deployment Checklist - Final

- [ ] All tests passing in CI/CD
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Security headers configured
- [ ] Monitoring & logging enabled
- [ ] Backups configured
- [ ] DNS records updated
- [ ] Smoke tests passing
- [ ] Performance baseline established
- [ ] Team trained on deployment process
- [ ] Disaster recovery plan documented

---

**Version**: 1.0.0
**Last Updated**: 2025-11-20
**Status**: Ready for Production Deployment ✅

For additional questions or issues, see `docs/testing/e2e_testing_roadmap.md` or `docs/testing/manual_e2e_testing_guide.md`
