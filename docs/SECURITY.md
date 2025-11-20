# Security Hardening Guide

Copy This v2.0 Backend - Comprehensive Security Implementation

## Table of Contents

1. [Overview](#overview)
2. [CORS Configuration](#cors-configuration)
3. [Input Validation](#input-validation)
4. [Secrets Management](#secrets-management)
5. [CSRF Protection](#csrf-protection)
6. [Retry Logic & Circuit Breaker](#retry-logic--circuit-breaker)
7. [Rate Limiting](#rate-limiting)
8. [Production Deployment](#production-deployment)
9. [Security Checklist](#security-checklist)

---

## Overview

This document describes the security hardening measures implemented in Copy This v2.0 to protect against common web application vulnerabilities.

### Security Features

✅ **CORS Hardening** - Explicit allow-list for methods and headers
✅ **Magic Number Validation** - File type verification via binary headers
✅ **Filename Sanitization** - Path traversal prevention
✅ **Secrets Management** - AWS/Vault support for encrypted key storage
✅ **CSRF Protection** - Double Submit Cookie pattern
✅ **Retry Logic** - Automatic retry with exponential backoff
✅ **Circuit Breaker** - Prevents cascading failures
✅ **Rate Limiting** - Per-IP request limits
✅ **Request Throttling** - Concurrent request limits

---

## CORS Configuration

**File:** `backend/main.py`

### Implementation

```python
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^(http://localhost:\d+|http://127\.0\.0\.1:\d+|https://.*\.loca\.lt)$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit only
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining", "X-Throttle-Active"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

### Security Benefits

- **No wildcard methods**: Only explicit HTTP methods allowed
- **Restricted headers**: Only necessary headers permitted
- **Credential support**: Enables secure cookie-based authentication
- **Origin regex**: Strict origin validation for localhost and deployment domains

### Configuration

No configuration required. Update `allow_origin_regex` for production domains:

```python
# Production example
allow_origin_regex=r"^https://(www\.)?yourdomain\.com$"
```

---

## Input Validation

**File:** `backend/security.py`

### Magic Number Validation

Validates file types using binary headers (magic numbers) instead of relying on Content-Type headers, which can be spoofed.

```python
from security import validate_image_upload

# In your endpoint
for file in files:
    await validate_image_upload(file)
```

### Features

1. **Magic Number Detection**: Reads first 2048 bytes to determine true file type
2. **Size Validation**: Max 10MB per file
3. **MIME Type Whitelist**: Only PNG, JPEG, WebP allowed
4. **Filename Sanitization**: Removes path traversal characters

### Example Attack Prevention

```python
# Attack: Upload PHP shell disguised as image
# File: evil.php (Content-Type: image/png)
# Magic bytes: <?php system($_GET['cmd']); ?>

# Detection:
detected_mime = magic.from_buffer(file_header, mime=True)
# Result: "text/x-php" → REJECTED ✅
```

### Filename Sanitization

Prevents path traversal attacks:

```python
from security import sanitize_filename

# Attack inputs → Safe outputs
"../../etc/passwd"           → "etc_passwd"
"<script>alert(1)</script>"  → "_script_alert_1___script_"
".hidden"                     → "hidden"
```

### Configuration

```python
# backend/security.py

# Allowed MIME types
ALLOWED_IMAGE_MIMES = {
    "image/png",
    "image/jpeg",
    "image/webp"
}

# Maximum file size
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

---

## Secrets Management

**File:** `backend/secrets_manager.py`

### Overview

Supports three backends for secure API key storage:

1. **Environment Variables** (default, development)
2. **AWS Secrets Manager** (production, cloud-native)
3. **HashiCorp Vault** (production, self-hosted)

### Backend Selection

Automatically detected based on environment:

```bash
# HashiCorp Vault (highest priority)
export VAULT_ADDR="https://vault.example.com:8200"
export VAULT_TOKEN="s.xxxxx"

# AWS Secrets Manager (second priority)
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"

# Environment Variables (fallback)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Usage

#### Option 1: Auto-load on Startup (Recommended)

```bash
# Enable secrets manager
export USE_SECRETS_MANAGER=true

# Start application
python -m uvicorn backend.main:app
```

The application will automatically load secrets during startup.

#### Option 2: Manual Loading

```python
from config import settings

# Load secrets programmatically
await settings.load_secrets()
```

### AWS Secrets Manager Setup

```bash
# 1. Install boto3
pip install boto3

# 2. Create secrets in AWS
aws secretsmanager create-secret \
    --name OPENAI_API_KEY \
    --secret-string "sk-..." \
    --region us-east-1

aws secretsmanager create-secret \
    --name ANTHROPIC_API_KEY \
    --secret-string "sk-ant-..." \
    --region us-east-1

# 3. Configure credentials
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"

# 4. Enable secrets manager
export USE_SECRETS_MANAGER=true
```

### HashiCorp Vault Setup

```bash
# 1. Install hvac
pip install hvac

# 2. Start Vault (or use existing)
vault server -dev

# 3. Store secrets
export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="s.xxxxx"

vault kv put secret/openai-api-key value="sk-..."
vault kv put secret/anthropic-api-key value="sk-ant-..."

# 4. Configure application
export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="s.xxxxx"
export VAULT_MOUNT_POINT="secret"  # KV mount point
export USE_SECRETS_MANAGER=true
```

### Security Benefits

- ✅ API keys never in code or version control
- ✅ Encrypted at rest (AWS/Vault)
- ✅ Centralized key management
- ✅ Access logging and auditing
- ✅ Automatic rotation support
- ✅ In-memory caching with TTL (5 minutes)

### Key Rotation

```python
from secrets_manager import get_secrets_manager

# Clear cache to force reload
manager = get_secrets_manager()
manager.clear_cache()

# Next call will fetch fresh keys
await settings.load_secrets(force_reload=True)
```

---

## CSRF Protection

**File:** `backend/csrf_protection.py`

### Overview

Protects against Cross-Site Request Forgery using the Double Submit Cookie pattern.

### How It Works

1. **GET request** → Server generates CSRF token, sets cookie + header
2. **POST/PUT/DELETE** → Client must include token in `X-CSRF-Token` header
3. **Token validation** → Server compares cookie and header
4. **Mismatch** → 403 Forbidden

### Configuration

```bash
# Enable CSRF protection (disabled by default)
export CSRF_ENABLED=true

# Generate secret key (run once)
python -c "from backend.csrf_protection import generate_csrf_secret_key; print(generate_csrf_secret_key())"

# Store in secrets manager or environment
export CSRF_SECRET_KEY="your-generated-key-here"

# Production settings
export CSRF_COOKIE_SECURE=true     # Require HTTPS
export CSRF_COOKIE_SAMESITE=strict  # Strict SameSite policy
export CSRF_TOKEN_TTL=3600          # Token expires after 1 hour
```

### Frontend Integration (React)

```javascript
// Get CSRF token from cookie
const getCsrfToken = () => {
    const cookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookie;
};

// Include token in fetch requests
const response = await fetch('/api/extract', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getCsrfToken()  // Required!
    },
    body: JSON.stringify(data),
    credentials: 'include'  // Include cookies
});
```

### Exempt Paths

Certain endpoints are automatically exempt from CSRF checks:

- `/health` - Health check
- `/docs`, `/redoc`, `/openapi.json` - API documentation
- `/api/extract/progressive` - WebSocket endpoint
- `/api/metrics/*` - Metrics endpoints

Add custom exempt paths in `main.py`:

```python
app.add_middleware(
    CSRFMiddleware,
    secret_key=csrf_secret,
    exempt_paths={
        "/health",
        "/api/webhooks/",  # Add custom paths
    }
)
```

---

## Retry Logic & Circuit Breaker

**Files:** `backend/retry_utils.py`, `backend/circuit_breaker.py`

### Retry Logic

Automatically retries failed requests with exponential backoff.

#### Decorators

```python
from retry_utils import (
    retry_network_errors,      # Network/timeout errors
    retry_external_api_errors,  # AI API failures
    retry_database_errors,      # DB connection issues
    retry_on_rate_limit,        # Rate limits (respects Retry-After)
)

# Example: AI API call with retry
@retry_external_api_errors(max_attempts=3, min_wait=4, max_wait=30)
async def call_gpt4_api():
    response = await openai.chat.completions.create(...)
    return response

# Example: Database operation with retry
@retry_database_errors(max_attempts=5, min_wait=1, max_wait=5)
async def save_to_db(session, data):
    session.add(data)
    await session.commit()
```

#### Configuration

| Decorator | Max Attempts | Wait Range | Use For |
|-----------|--------------|------------|---------|
| `retry_network_errors` | 3 | 2-10s | HTTP requests, WebSocket |
| `retry_external_api_errors` | 3 | 4-30s | AI APIs (OpenAI, Anthropic) |
| `retry_database_errors` | 5 | 1-5s | SQLAlchemy operations |
| `retry_on_rate_limit` | 3 | 30-120s | Rate-limited APIs |

### Circuit Breaker

Prevents cascading failures by blocking requests to failing services.

#### States

```
CLOSED (normal) → OPEN (blocking) → HALF_OPEN (testing) → CLOSED
                    ↑                      ↓
                    └──── 3 failures      2 successes ────┘
```

#### Configuration

```python
from circuit_breaker import CircuitBreaker

# Create custom breaker
breaker = CircuitBreaker(
    name="my_service",
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=60.0,    # Test recovery after 60s
    success_threshold=2,      # Close after 2 successes
)

@breaker
async def call_external_service():
    # Your code here
    pass
```

#### Pre-configured Breakers

- `gpt4_vision_breaker` - GPT-4 Vision API
- `claude_vision_breaker` - Claude Vision API
- `openai_api_breaker` - OpenAI API
- `anthropic_api_breaker` - Anthropic API

#### Monitoring

```python
from circuit_breaker import get_all_breaker_stats

# Get stats for all breakers
stats = get_all_breaker_stats()
for service, state in stats.items():
    print(f"{service}: {state['state']} (failures: {state['failure_count']})")
```

---

## Rate Limiting

**Files:** `backend/rate_limiting.py`, `backend/main.py`

### Per-IP Rate Limiting

```python
# Default: 100 requests per minute per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Per-endpoint limits
@router.post("/extract")
@limiter.limit("10/minute")  # More restrictive for expensive endpoints
async def extract_tokens(request: Request, files: List[UploadFile]):
    ...
```

### Token Bucket Algorithm

Advanced rate limiting with burst support:

```python
rate_limit_config = RateLimitConfig(
    requests_per_second=10.0,  # 10 RPS sustained
    burst_size=20,             # Allow bursts up to 20 requests
    enabled=True
)
```

### Request Throttling

Limits concurrent requests system-wide:

```python
app.add_middleware(
    ThrottlingMiddleware,
    max_concurrent=100,   # Max 100 concurrent requests
    max_queue_size=500,   # Queue up to 500 requests
    queue_timeout=30.0    # 30 second queue timeout
)
```

---

## Production Deployment

### Environment Variables Checklist

```bash
# Application
USE_SECRETS_MANAGER=true
LOG_LEVEL=info

# CSRF Protection
CSRF_ENABLED=true
CSRF_SECRET_KEY=your-generated-secret
CSRF_COOKIE_SECURE=true
CSRF_COOKIE_SAMESITE=strict

# Secrets Manager (AWS)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1

# OR Secrets Manager (Vault)
VAULT_ADDR=https://vault.example.com:8200
VAULT_TOKEN=s.xxxxx
VAULT_MOUNT_POINT=secret

# API Keys (if using env vars instead of secrets manager)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Environment
ENV USE_SECRETS_MANAGER=true
ENV CSRF_ENABLED=true
ENV LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: copy-this-backend
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: backend
        image: copy-this-backend:latest
        env:
        - name: USE_SECRETS_MANAGER
          value: "true"
        - name: CSRF_ENABLED
          value: "true"
        - name: AWS_REGION
          value: "us-east-1"
        # Secrets mounted from AWS Secrets Manager CSI Driver
        volumeMounts:
        - name: secrets
          mountPath: /mnt/secrets
          readOnly: true
      volumes:
      - name: secrets
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
```

---

## Security Checklist

### Pre-Deployment

- [ ] CORS configuration updated for production domains
- [ ] CSRF protection enabled (`CSRF_ENABLED=true`)
- [ ] CSRF secret key generated and stored securely
- [ ] Secrets manager configured (AWS/Vault)
- [ ] API keys removed from environment variables
- [ ] SSL/TLS enabled (`CSRF_COOKIE_SECURE=true`)
- [ ] Rate limits configured appropriately
- [ ] Circuit breakers tested
- [ ] File upload limits enforced
- [ ] Logging enabled (JSON format for production)

### Post-Deployment

- [ ] Monitor circuit breaker states
- [ ] Review rate limit metrics
- [ ] Check CSRF token validation rates
- [ ] Audit secrets manager access logs
- [ ] Verify retry logic is working
- [ ] Test file upload validation
- [ ] Review error logs for security events
- [ ] Set up alerting for security violations

### Regular Maintenance

- [ ] Rotate API keys quarterly
- [ ] Update dependencies monthly (run `pip-audit`)
- [ ] Review CORS origins
- [ ] Audit secrets manager permissions
- [ ] Test circuit breaker recovery
- [ ] Review rate limit thresholds
- [ ] Update security documentation

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Guide](https://fastapi.tiangolo.com/tutorial/security/)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [HashiCorp Vault](https://www.vaultproject.io/docs)
- [CSRF Protection](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

## Support

For security issues, please contact the security team or open an issue on GitHub.

**Do not publicly disclose security vulnerabilities.**
