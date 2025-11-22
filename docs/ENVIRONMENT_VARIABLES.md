# Environment Variables Configuration

This document describes all environment variables required for the Copy That platform across different deployment environments.

## Required Variables

### Authentication & Security

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `SECRET_KEY` | JWT signing key (min 32 chars) | **Yes** | None | `your-super-secret-key-min-32-chars` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | No | `30` | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | No | `7` | `30` |

### Database

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | **Yes** | None | `postgresql+asyncpg://user:pass@host/db` |

### Redis (Caching & Rate Limiting)

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `REDIS_URL` | Redis connection string | No | None | `redis://localhost:6379/0` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | No | `true` | `false` |

> **Note**: If `REDIS_URL` is not set, caching and rate limiting will be disabled gracefully.

### AI/ML Integration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | **Yes** | None | `sk-ant-...` |

### Google Cloud Platform

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `GCP_PROJECT_ID` | GCP project identifier | No | `copy-that-platform` | `my-project` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | No | None | `/path/to/sa.json` |

### Application Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `ENVIRONMENT` | Deployment environment | No | `local` | `production` |
| `PORT` | Server port | No | `8000` | `8080` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | No | `http://localhost:5173,...` | `https://app.example.com` |

## Environment-Specific Configuration

### Local Development

```bash
# .env.local
ENVIRONMENT=local
SECRET_KEY=dev-secret-key-at-least-32-characters-long
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/copythat
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-your-dev-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
```

### CI/Testing

```bash
# .env.ci
ENVIRONMENT=testing
SECRET_KEY=ci-test-secret-key-at-least-32-characters
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/copythat_test
REDIS_URL=redis://localhost:6379/1
ANTHROPIC_API_KEY=sk-ant-test-key
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=1
RATE_LIMIT_ENABLED=false
```

### Staging

```bash
# Configure in Cloud Run or CI/CD secrets
ENVIRONMENT=staging
SECRET_KEY=<generate-secure-random-string>
DATABASE_URL=<neon-staging-connection-string>
REDIS_URL=<redis-cloud-staging-url>
ANTHROPIC_API_KEY=<staging-api-key>
GCP_PROJECT_ID=copy-that-staging
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=https://staging.copythat.app
```

### Production

```bash
# Configure in Cloud Run secrets or Secret Manager
ENVIRONMENT=production
SECRET_KEY=<generate-secure-random-string-64-chars>
DATABASE_URL=<neon-production-connection-string>
REDIS_URL=<redis-cloud-production-url>
ANTHROPIC_API_KEY=<production-api-key>
GCP_PROJECT_ID=copy-that-platform
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=https://copythat.app,https://www.copythat.app
```

## Generating Secure Keys

### SECRET_KEY Generation

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Using OpenSSL
openssl rand -base64 48
```

## Cloud Run Configuration

### Setting Environment Variables

```bash
# Using gcloud CLI
gcloud run services update copy-that \
  --set-env-vars "ENVIRONMENT=production" \
  --set-env-vars "SECRET_KEY=your-secret" \
  --set-env-vars "DATABASE_URL=your-db-url"

# Using secrets (recommended for sensitive values)
gcloud run services update copy-that \
  --set-secrets "SECRET_KEY=secret-key:latest" \
  --set-secrets "DATABASE_URL=database-url:latest" \
  --set-secrets "ANTHROPIC_API_KEY=anthropic-key:latest"
```

### GitHub Actions Secrets

For CI/CD pipelines, configure these secrets in GitHub repository settings:

- `SECRET_KEY` - JWT signing key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (optional)
- `ANTHROPIC_API_KEY` - Claude API key
- `GCP_PROJECT_ID` - Google Cloud project ID
- `GCP_SA_KEY` - Service account JSON (base64 encoded)

## Validation

The application validates required environment variables at startup. Missing required variables will:

1. **Authentication**: Raise startup error if `SECRET_KEY` is missing
2. **Database**: Raise startup error if `DATABASE_URL` is missing
3. **Redis**: Log warning and disable caching/rate limiting if `REDIS_URL` is missing
4. **AI/ML**: Raise error on API call if `ANTHROPIC_API_KEY` is missing

## Health Check

Use the `/health` endpoint to verify configuration:

```bash
curl https://your-app/health
```

Response includes environment status and version information.
