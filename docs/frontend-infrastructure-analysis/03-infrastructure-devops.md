# Infrastructure & DevOps Analysis

> Deep dive into Docker, Terraform, CI/CD, GCP Cloud Run, and observability

---

## Table of Contents

1. [Docker Optimization](#docker-optimization)
2. [Terraform Infrastructure](#terraform-infrastructure)
3. [GCP Cloud Run Configuration](#gcp-cloud-run-configuration)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Observability & Monitoring](#observability--monitoring)
6. [Cost Analysis](#cost-analysis)
7. [Security Hardening](#security-hardening)

---

## Docker Optimization

### Current Dockerfile Analysis

**Production Dockerfile (4-stage multi-stage build):**

```dockerfile
# Stage 1: base
FROM python:3.12-slim AS base
RUN pip install uv
COPY pyproject.toml README.md ./

# Stage 2: development
FROM base AS development
RUN uv pip install -e ".[dev]"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]

# Stage 3: builder
FROM base AS builder
RUN uv pip install .

# Stage 4: production
FROM python:3.12-slim AS production
RUN useradd -m -u 1000 appuser
USER appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
HEALTHCHECK CMD httpx http://localhost:${PORT:-8000}/health
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.UvicornWorker", "-w", "4"]
```

### ✅ Strengths

1. **Non-root user** - Security best practice
2. **Health check** - Enables proper orchestration
3. **uv package manager** - 10-100x faster than pip
4. **Multi-stage** - Smaller production image

### ⚠️ Issues & Improvements

#### 1. Base Image Optimization

**Current:**
```dockerfile
FROM python:3.12-slim AS base
```

**Optimized:**
```dockerfile
# Use specific version for reproducibility
FROM python:3.12.3-slim-bookworm AS base

# Install security updates
RUN apt-get update && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*
```

#### 2. Layer Caching Optimization

**Current Order:**
```dockerfile
COPY pyproject.toml README.md ./
RUN uv pip install .
COPY . .
```

**Optimized Order:**
```dockerfile
# Copy dependency files first (changes less frequently)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies (cached if files unchanged)
RUN uv pip install --frozen --no-cache

# Copy application code last (changes most frequently)
COPY app/ ./app/
```

#### 3. Production Image Hardening

**Recommended Production Stage:**
```dockerfile
FROM python:3.12.3-slim-bookworm AS production

# Security: Remove unnecessary packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create non-root user
RUN groupadd -g 1000 appgroup \
    && useradd -u 1000 -g appgroup -s /bin/false -M appuser

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder --chown=appuser:appgroup /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder --chown=appuser:appgroup /app ./

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

USER appuser

# Health check with timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.UvicornWorker", \
     "-w", "4", \
     "-b", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--enable-stdio-inheritance"]
```

### Image Size Reduction

**Strategy 1: Distroless Base**
```dockerfile
# Even smaller than slim
FROM gcr.io/distroless/python3-debian12 AS production

# Only Python + your code, no shell, no package manager
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app

WORKDIR /app
USER nonroot

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.UvicornWorker"]
```

**Strategy 2: Multi-platform Builds**
```dockerfile
# syntax=docker/dockerfile:1.4

FROM --platform=$BUILDPLATFORM python:3.12-slim AS builder
ARG TARGETPLATFORM
ARG BUILDPLATFORM
```

### Docker Compose Improvements

**Current docker-compose.yml snippets with issues:**

```yaml
services:
  api:
    build:
      context: .
      target: development
    volumes:
      - .:/app  # ⚠️ Mounts entire repo
    depends_on:
      - postgres
      - redis
```

**Improved Configuration:**
```yaml
version: '3.9'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
      cache_from:
        - type=registry,ref=us-central1-docker.pkg.dev/copy-that/images/api:cache
    volumes:
      # Only mount source code, not dependencies
      - ./app:/app/app:cached
      - ./alembic:/app/alembic:cached
      - ./pyproject.toml:/app/pyproject.toml:ro
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/copy_that
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
    ports:
      - "8000:8000"
    networks:
      - backend

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: copy_that
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./deploy/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    ports:
      - "5432:5432"
    networks:
      - backend

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    ports:
      - "6379:6379"
    networks:
      - backend

networks:
  backend:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

---

## Terraform Infrastructure

### Current Module Structure

```
deploy/terraform/
├── main.tf              # Provider, APIs, IAM, Workload Identity
├── variables.tf         # Input variables (25+)
├── outputs.tf           # Outputs (15+)
├── networking.tf        # VPC, subnets, NAT, firewall
├── cloudsql.tf          # PostgreSQL
├── redis.tf             # Memorystore
├── artifact_registry.tf # Docker registry
└── cloudrun.tf          # Service, jobs, scheduler
```

### ✅ Strengths

1. **Remote state** in GCS with versioning
2. **Workload Identity** for GitHub Actions (no long-lived keys)
3. **Comprehensive networking** with private VPC
4. **Secrets in Secret Manager**

### ⚠️ Issues & Improvements

#### 1. State Management Enhancement

**Current:**
```hcl
terraform {
  backend "gcs" {
    bucket = "copy-that-terraform-state"
    prefix = "terraform/state"
  }
}
```

**Improved with Encryption:**
```hcl
terraform {
  backend "gcs" {
    bucket  = "copy-that-terraform-state"
    prefix  = "terraform/state"

    # Enable encryption
    encryption_key = "projects/my-project/locations/global/keyRings/terraform-state/cryptoKeys/terraform-state-key"
  }
}

# Create KMS key for state encryption
resource "google_kms_key_ring" "terraform_state" {
  name     = "terraform-state"
  location = "global"
}

resource "google_kms_crypto_key" "terraform_state" {
  name            = "terraform-state-key"
  key_ring        = google_kms_key_ring.terraform_state.id
  rotation_period = "7776000s" # 90 days

  lifecycle {
    prevent_destroy = true
  }
}
```

#### 2. Database Configuration

**Current (Staging):**
```hcl
resource "google_sql_database_instance" "main" {
  database_version = "POSTGRES_16"
  tier             = "db-f1-micro"  # ⚠️ Shared CPU

  settings {
    availability_type = "ZONAL"  # ⚠️ No HA
  }
}
```

**Improved Production Configuration:**
```hcl
resource "google_sql_database_instance" "main" {
  name             = "${var.project_id}-db-${var.environment}"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier              = var.environment == "production" ? "db-custom-2-7680" : "db-f1-micro"
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = var.environment == "production" ? 100 : 10
    disk_autoresize   = true

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = var.environment == "production"
      start_time                     = "03:00"

      backup_retention_settings {
        retained_backups = var.environment == "production" ? 30 : 7
        retention_unit   = "COUNT"
      }
    }

    maintenance_window {
      day          = 7  # Sunday
      hour         = 3  # 3 AM
      update_track = "stable"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 4500
      record_application_tags = true
      record_client_address   = false
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id

      dynamic "authorized_networks" {
        for_each = var.environment == "production" ? [] : var.authorized_networks
        content {
          name  = authorized_networks.value.name
          value = authorized_networks.value.cidr
        }
      }
    }

    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"  # Log queries > 1s
    }

    database_flags {
      name  = "max_connections"
      value = var.environment == "production" ? "200" : "50"
    }
  }

  deletion_protection = var.environment == "production"

  lifecycle {
    prevent_destroy = var.environment == "production"
  }
}

# Read replica for production
resource "google_sql_database_instance" "read_replica" {
  count = var.environment == "production" ? 1 : 0

  name                 = "${var.project_id}-db-replica-${var.environment}"
  master_instance_name = google_sql_database_instance.main.name
  region               = var.region
  database_version     = "POSTGRES_16"

  replica_configuration {
    failover_target = false
  }

  settings {
    tier              = "db-custom-2-7680"
    availability_type = "ZONAL"
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
  }
}
```

#### 3. Redis Configuration

**Current:**
```hcl
resource "google_redis_instance" "main" {
  tier           = "BASIC"  # ⚠️ No HA
  memory_size_gb = 1
}
```

**Improved:**
```hcl
resource "google_redis_instance" "main" {
  name           = "${var.project_id}-redis-${var.environment}"
  tier           = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  memory_size_gb = var.environment == "production" ? 5 : 1
  region         = var.region

  # Enables automatic failover
  replica_count = var.environment == "production" ? 1 : 0
  read_replicas_mode = var.environment == "production" ? "READ_REPLICAS_ENABLED" : "READ_REPLICAS_DISABLED"

  authorized_network = google_compute_network.vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_version = "REDIS_7_0"

  redis_configs = {
    "maxmemory-policy"       = "allkeys-lru"
    "notify-keyspace-events" = "Ex"  # For session expiry
    "activedefrag"           = "yes"
  }

  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}
```

#### 4. Workload Identity Security

**Current Issue:** Same principal for staging/production

```hcl
# Current - allows any branch to deploy
resource "google_iam_workload_identity_pool_provider" "github" {
  attribute_mapping = {
    "attribute.repository" = "assertion.repository"
  }
}

resource "google_service_account_iam_binding" "workload_identity" {
  members = [
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repository}"
  ]
}
```

**Improved with Branch Constraints:**
```hcl
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
    "attribute.environment" = "assertion.environment"
  }

  attribute_condition = "assertion.repository == '${var.github_repository}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Separate service accounts per environment
resource "google_service_account" "github_actions_staging" {
  account_id   = "github-actions-staging"
  display_name = "GitHub Actions - Staging"
}

resource "google_service_account" "github_actions_production" {
  account_id   = "github-actions-production"
  display_name = "GitHub Actions - Production"
}

# Staging: Only allow develop branch
resource "google_service_account_iam_binding" "staging_workload_identity" {
  service_account_id = google_service_account.github_actions_staging.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.ref/refs/heads/develop"
  ]
}

# Production: Only allow main branch
resource "google_service_account_iam_binding" "production_workload_identity" {
  service_account_id = google_service_account.github_actions_production.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.ref/refs/heads/main"
  ]
}
```

### Infrastructure Testing

**Add to CI Pipeline:**
```yaml
terraform-validate:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - uses: hashicorp/setup-terraform@v3
      with:
        terraform_version: 1.6.0

    - name: Terraform Format Check
      run: terraform fmt -check -recursive
      working-directory: deploy/terraform

    - name: Terraform Init
      run: terraform init -backend=false
      working-directory: deploy/terraform

    - name: Terraform Validate
      run: terraform validate
      working-directory: deploy/terraform

    - name: TFLint
      uses: terraform-linters/setup-tflint@v4

    - name: Run TFLint
      run: tflint --recursive
      working-directory: deploy/terraform

    - name: Checkov Security Scan
      uses: bridgecrewio/checkov-action@v12
      with:
        directory: deploy/terraform
        framework: terraform
        soft_fail: false
```

---

## GCP Cloud Run Configuration

### Current Configuration Analysis

**Terraform Cloud Run Service:**
```hcl
resource "google_cloud_run_v2_service" "api" {
  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/images/api:latest"

      resources {
        limits = {
          cpu    = var.environment == "production" ? "2" : "1"
          memory = var.environment == "production" ? "1Gi" : "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = var.environment == "production" ? 1 : 0
      max_instance_count = var.environment == "production" ? 100 : 10
    }
  }
}
```

### ✅ Strengths

1. Environment-specific resource allocation
2. Auto-scaling configuration
3. Secrets from Secret Manager

### ⚠️ Issues & Improvements

#### 1. Cold Start Mitigation

**Current Issue:** min_instances = 0 for staging causes ~10s cold starts

**Improved Configuration:**
```hcl
resource "google_cloud_run_v2_service" "api" {
  name     = "${var.project_id}-api-${var.environment}"
  location = var.region

  template {
    # Startup CPU boost for faster cold starts
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/images/api:${var.image_tag}"

      resources {
        limits = {
          cpu    = var.environment == "production" ? "2" : "1"
          memory = var.environment == "production" ? "1Gi" : "512Mi"
        }
        cpu_idle = var.environment == "production" ? false : true
        startup_cpu_boost = true  # NEW: 2x CPU during startup
      }

      # Startup probe - more lenient for cold starts
      startup_probe {
        initial_delay_seconds = 0
        timeout_seconds       = 10
        period_seconds        = 3
        failure_threshold     = 10

        http_get {
          path = "/health"
          port = 8000
        }
      }

      # Liveness probe - stricter for running container
      liveness_probe {
        timeout_seconds   = 5
        period_seconds    = 15
        failure_threshold = 3

        http_get {
          path = "/health"
          port = 8000
        }
      }

      # Environment variables
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "LOG_LEVEL"
        value = var.environment == "production" ? "INFO" : "DEBUG"
      }

      # Secrets
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "REDIS_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.redis_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.app_secret.secret_id
            version = "latest"
          }
        }
      }
    }

    # Request timeout
    timeout = "300s"

    # Concurrency
    max_instance_request_concurrency = 80

    # Scaling
    scaling {
      min_instance_count = var.environment == "production" ? 1 : 0
      max_instance_count = var.environment == "production" ? 100 : 10
    }

    # VPC connector for private resources
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    # Service account
    service_account = google_service_account.cloud_run.email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,  # Managed by CI/CD
    ]
  }
}
```

#### 2. Traffic Splitting for Canary Deployments

```hcl
resource "google_cloud_run_v2_service" "api" {
  # ... container config ...

  # Canary deployment
  traffic {
    type     = "TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION"
    revision = google_cloud_run_v2_service.api.template[0].revision
    percent  = 90
    tag      = "stable"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 10
    tag     = "canary"
  }
}

# Output canary URL for testing
output "canary_url" {
  value = "https://canary---${google_cloud_run_v2_service.api.name}-${random_string.suffix.result}.a.run.app"
}
```

#### 3. Cost Optimization

```hcl
# Use scheduled scaling for off-hours
resource "google_cloud_scheduler_job" "scale_down" {
  count = var.environment == "production" ? 1 : 0

  name        = "scale-down-${var.environment}"
  schedule    = "0 22 * * *"  # 10 PM daily
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = "https://run.googleapis.com/v2/${google_cloud_run_v2_service.api.id}:setIamPolicy"
    http_method = "PATCH"

    body = base64encode(jsonencode({
      template = {
        scaling = {
          minInstanceCount = 0
          maxInstanceCount = 10
        }
      }
    }))

    oauth_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}

resource "google_cloud_scheduler_job" "scale_up" {
  count = var.environment == "production" ? 1 : 0

  name        = "scale-up-${var.environment}"
  schedule    = "0 6 * * 1-5"  # 6 AM weekdays
  time_zone   = "America/Los_Angeles"

  http_target {
    uri         = "https://run.googleapis.com/v2/${google_cloud_run_v2_service.api.id}:setIamPolicy"
    http_method = "PATCH"

    body = base64encode(jsonencode({
      template = {
        scaling = {
          minInstanceCount = 2
          maxInstanceCount = 100
        }
      }
    }))

    oauth_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}
```

---

## CI/CD Pipeline

### Current Pipeline Architecture

```
Push → CI (security, lint, test, docker) → Build → Deploy
```

### Pipeline Issues

#### 1. Security Scans Don't Block

**Current (non-blocking):**
```yaml
- name: Run pip-audit
  run: pip-audit --require-hashes
  continue-on-error: true  # ⚠️ Never fails

- name: Run Bandit
  run: bandit -r app -f json
  continue-on-error: true  # ⚠️ Never fails
```

**Improved (blocking with thresholds):**
```yaml
security:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install pip-audit bandit safety

    # Block on high/critical vulnerabilities
    - name: Run pip-audit
      run: |
        pip-audit --require-hashes --strict \
          --ignore-vuln PYSEC-2022-XXXXX \  # Known false positives
          --desc on

    # Block on high severity issues
    - name: Run Bandit
      run: |
        bandit -r app -f json -o bandit-report.json \
          --severity-level high \
          --confidence-level high

        # Fail if any high severity issues
        if jq -e '.results | length > 0' bandit-report.json; then
          echo "::error::Bandit found high severity security issues"
          cat bandit-report.json | jq
          exit 1
        fi

    - name: Run Safety Check
      run: |
        safety check --full-report

    - name: Run Gitleaks
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    - name: Upload security reports
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: security-reports
        path: |
          bandit-report.json
```

#### 2. No Automated Rollback

**Current:** Deployment continues even if smoke tests fail

**Improved Deploy Workflow:**
```yaml
deploy-production:
  runs-on: ubuntu-latest
  environment: production
  needs: [build-and-push]

  steps:
    - uses: actions/checkout@v4

    - name: Authenticate to GCP
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ vars.WORKLOAD_IDENTITY_PROVIDER }}
        service_account: ${{ vars.SERVICE_ACCOUNT }}

    - name: Setup gcloud
      uses: google-github-actions/setup-gcloud@v2

    # Get current revision for rollback
    - name: Get current revision
      id: current
      run: |
        REVISION=$(gcloud run services describe ${{ vars.SERVICE_NAME }} \
          --region ${{ vars.REGION }} \
          --format 'value(status.latestReadyRevisionName)')
        echo "revision=$REVISION" >> $GITHUB_OUTPUT

    # Deploy new revision
    - name: Deploy to Cloud Run
      id: deploy
      uses: google-github-actions/deploy-cloudrun@v2
      with:
        service: ${{ vars.SERVICE_NAME }}
        region: ${{ vars.REGION }}
        image: ${{ needs.build-and-push.outputs.image }}
        flags: |
          --cpu=2
          --memory=1Gi
          --min-instances=1
          --max-instances=100
          --no-traffic

    # Run smoke tests against new revision
    - name: Run smoke tests
      id: smoke
      run: |
        NEW_URL="${{ steps.deploy.outputs.url }}"

        # Test health endpoint
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$NEW_URL/health")
        if [ "$HTTP_CODE" != "200" ]; then
          echo "::error::Health check failed with status $HTTP_CODE"
          exit 1
        fi

        # Test API status
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$NEW_URL/api/status")
        if [ "$HTTP_CODE" != "200" ]; then
          echo "::error::API status check failed with status $HTTP_CODE"
          exit 1
        fi

        # Test critical endpoint with POST
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
          -X POST "$NEW_URL/api/projects" \
          -H "Content-Type: application/json" \
          -d '{"name": "smoke-test"}')
        if [ "$HTTP_CODE" != "201" ] && [ "$HTTP_CODE" != "200" ]; then
          echo "::error::Create project failed with status $HTTP_CODE"
          exit 1
        fi

        echo "All smoke tests passed!"

    # Route traffic to new revision
    - name: Route traffic to new revision
      if: success()
      run: |
        gcloud run services update-traffic ${{ vars.SERVICE_NAME }} \
          --region ${{ vars.REGION }} \
          --to-latest

    # Rollback on failure
    - name: Rollback on failure
      if: failure() && steps.smoke.outcome == 'failure'
      run: |
        echo "::warning::Rolling back to previous revision: ${{ steps.current.outputs.revision }}"

        gcloud run services update-traffic ${{ vars.SERVICE_NAME }} \
          --region ${{ vars.REGION }} \
          --to-revisions ${{ steps.current.outputs.revision }}=100

        # Delete failed revision
        gcloud run revisions delete ${{ steps.deploy.outputs.revision }} \
          --region ${{ vars.REGION }} \
          --quiet

        echo "::error::Deployment failed and was rolled back"

    # Create release
    - name: Create GitHub Release
      if: success() && github.ref_type == 'tag'
      uses: softprops/action-gh-release@v1
      with:
        generate_release_notes: true
```

#### 3. Parallel Job Optimization

**Current:** Jobs run sequentially

**Improved with Matrix and Caching:**
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        tool: [ruff, mypy]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Run ${{ matrix.tool }}
        run: |
          pip install ${{ matrix.tool }}
          if [ "${{ matrix.tool }}" = "ruff" ]; then
            ruff check app
          else
            mypy app --strict
          fi

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-type: [unit, integration]
      fail-fast: false

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -e ".[test]"

      - name: Run ${{ matrix.test-type }} tests
        run: |
          if [ "${{ matrix.test-type }}" = "unit" ]; then
            pytest tests/unit -v --cov=app --cov-report=xml
          else
            pytest tests/integration -v --cov=app --cov-report=xml --cov-append
          fi

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
          flags: ${{ matrix.test-type }}
```

---

## Observability & Monitoring

### Current State

- **Local:** Prometheus + Grafana in docker-compose
- **Production:** No configured alerting
- **Logging:** stdout/stderr (Cloud Logging automatic)

### Recommended Monitoring Stack

#### 1. Structured Logging

**Python logging configuration:**
```python
# app/core/logging.py
import json
import logging
import sys
from datetime import datetime

class CloudLoggingFormatter(logging.Formatter):
    """Format logs for Google Cloud Logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO"):
    """Configure application logging."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(CloudLoggingFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(handler)

    # Set third-party loggers to WARNING
    for logger_name in ["uvicorn", "sqlalchemy", "httpx"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
```

#### 2. Cloud Monitoring Alerts

```hcl
# terraform/monitoring.tf

# Alert policy for high error rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate - ${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 5%"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        AND resource.labels.service_name = "${google_cloud_run_v2_service.api.name}"
        AND metric.type = "run.googleapis.com/request_count"
        AND metric.labels.response_code_class = "5xx"
      EOT

      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "604800s"  # 7 days
  }

  user_labels = {
    environment = var.environment
    severity    = "critical"
  }
}

# Alert policy for high latency
resource "google_monitoring_alert_policy" "high_latency" {
  display_name = "High Latency - ${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "P95 latency > 2s"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        AND resource.labels.service_name = "${google_cloud_run_v2_service.api.name}"
        AND metric.type = "run.googleapis.com/request_latencies"
      EOT

      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 2000  # 2 seconds

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_95"
        cross_series_reducer = "REDUCE_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.slack.id]
}

# Alert for database connections
resource "google_monitoring_alert_policy" "db_connections" {
  display_name = "Database Connection Pool Exhausted"
  combiner     = "OR"

  conditions {
    display_name = "Connections > 80%"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloudsql_database"
        AND resource.labels.database_id = "${var.project_id}:${google_sql_database_instance.main.name}"
        AND metric.type = "cloudsql.googleapis.com/database/postgresql/num_backends"
      EOT

      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 160  # 80% of 200 max_connections
    }
  }

  notification_channels = [google_monitoring_notification_channel.pagerduty.id]
}

# Notification channels
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Alerts"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}

resource "google_monitoring_notification_channel" "slack" {
  display_name = "Slack Alerts"
  type         = "slack"

  labels = {
    channel_name = "#alerts"
  }

  sensitive_labels {
    auth_token = var.slack_webhook_token
  }
}
```

#### 3. Custom Metrics

**FastAPI middleware for metrics:**
```python
# app/middleware/metrics.py
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

EXTRACTION_DURATION = Histogram(
    "color_extraction_duration_seconds",
    "Color extraction processing time",
    ["image_count"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status = response.status_code

        REQUEST_COUNT.labels(method, endpoint, status).inc()
        REQUEST_LATENCY.labels(method, endpoint).observe(duration)

        return response


async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

#### 4. Dashboard Configuration

**Grafana dashboard JSON:**
```json
{
  "title": "Copy-That API Dashboard",
  "panels": [
    {
      "title": "Request Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(http_requests_total[5m])",
          "legendFormat": "{{method}} {{endpoint}}"
        }
      ]
    },
    {
      "title": "Error Rate",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100"
        }
      ],
      "thresholds": {
        "steps": [
          {"color": "green", "value": 0},
          {"color": "yellow", "value": 1},
          {"color": "red", "value": 5}
        ]
      }
    },
    {
      "title": "P95 Latency",
      "type": "gauge",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
        }
      ],
      "unit": "s"
    },
    {
      "title": "Extraction Duration",
      "type": "heatmap",
      "targets": [
        {
          "expr": "rate(color_extraction_duration_seconds_bucket[5m])"
        }
      ]
    }
  ]
}
```

---

## Cost Analysis

### Current Estimated Costs

| Resource | Staging/mo | Production/mo | Notes |
|----------|------------|---------------|-------|
| Cloud Run | $5-15 | $50-200 | Based on traffic |
| Cloud SQL (db-f1-micro) | $7 | - | Shared CPU |
| Cloud SQL (db-custom-2-7680) | - | $50-150 | Dedicated |
| Memorystore BASIC | $15 | - | 1GB |
| Memorystore STANDARD_HA | - | $50-100 | 5GB |
| Artifact Registry | $1-5 | $5-10 | Storage |
| VPC/Networking | $5-10 | $20-50 | NAT, connectors |
| Secret Manager | $0.06/secret | $0.06/secret | Per version |
| **Total** | **$33-52** | **$175-510** | |

### Cost Optimization Opportunities

#### 1. Cloud Run Optimization
```hcl
# Use min instances = 0 for staging
scaling {
  min_instance_count = 0
  max_instance_count = 10
}

# Use CPU throttling when idle
resources {
  cpu_idle = true  # Reduces billing to memory-only
}
```

**Savings:** ~$20/month staging

#### 2. Scheduled Scaling
```hcl
# Scale down at night
resource "google_cloud_scheduler_job" "scale_down_night" {
  schedule = "0 22 * * *"  # 10 PM
  # Set min_instances to 0
}
```

**Savings:** ~$50/month production (for 8 hours/day)

#### 3. Artifact Registry Cleanup
```hcl
resource "google_artifact_registry_repository" "images" {
  cleanup_policies {
    id     = "delete-old-images"
    action = "DELETE"
    condition {
      older_than = "604800s"  # 7 days
      tag_state  = "UNTAGGED"
    }
  }
}
```

**Savings:** ~$5/month

#### 4. Budget Alerts

```hcl
resource "google_billing_budget" "project" {
  billing_account = var.billing_account
  display_name    = "copy-that-${var.environment}"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.environment == "production" ? "500" : "100"
    }
  }

  threshold_rules {
    threshold_percent = 0.5
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.9
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "FORECASTED_SPEND"
  }

  all_updates_rule {
    pubsub_topic         = google_pubsub_topic.budget_alerts.id
    schema_version       = "1.0"
    monitoring_notification_channels = [
      google_monitoring_notification_channel.email.id
    ]
  }
}
```

---

## Security Hardening

### Current Security Gaps

| Issue | Risk | Remediation |
|-------|------|-------------|
| Staging unauthenticated | Medium | Add IAP or auth |
| Security scans don't block | High | Remove continue-on-error |
| Same service account for envs | Medium | Separate accounts |
| No Cloud Armor | Medium | Add DDoS protection |

### Security Improvements

#### 1. Identity-Aware Proxy for Staging

```hcl
# Enable IAP for staging
resource "google_iap_web_iam_member" "staging_access" {
  count = var.environment == "staging" ? 1 : 0

  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "group:developers@company.com"
}

resource "google_compute_backend_service" "staging" {
  count = var.environment == "staging" ? 1 : 0

  iap {
    oauth2_client_id     = var.iap_client_id
    oauth2_client_secret = var.iap_client_secret
  }
}
```

#### 2. Cloud Armor WAF

```hcl
resource "google_compute_security_policy" "policy" {
  name = "${var.project_id}-security-policy"

  # Rate limiting
  rule {
    action   = "rate_based_ban"
    priority = 1000
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      rate_limit_threshold {
        count        = 1000
        interval_sec = 60
      }
      ban_duration_sec = 600
      conform_action   = "allow"
      exceed_action    = "deny(429)"
    }
  }

  # Block common attacks
  rule {
    action   = "deny(403)"
    priority = 2000
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
  }

  rule {
    action   = "deny(403)"
    priority = 2001
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-stable')"
      }
    }
  }

  # Default allow
  rule {
    action   = "allow"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
  }
}
```

#### 3. Secret Rotation

```hcl
# Enable automatic rotation
resource "google_secret_manager_secret" "app_secret" {
  secret_id = "app-secret-key"

  rotation {
    rotation_period    = "2592000s"  # 30 days
    next_rotation_time = timeadd(timestamp(), "720h")
  }

  topics {
    name = google_pubsub_topic.secret_rotation.id
  }
}

# Cloud Function to handle rotation
resource "google_cloudfunctions2_function" "rotate_secrets" {
  name     = "rotate-secrets"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "rotate_secret"
    source {
      storage_source {
        bucket = google_storage_bucket.functions.name
        object = google_storage_bucket_object.rotate_secrets.name
      }
    }
  }

  service_config {
    available_memory = "256M"
    timeout_seconds  = 60
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.secret_rotation.id
  }
}
```

---

## Summary

### Critical Actions

1. **Enable security scan blocking** - Prevent vulnerable deploys
2. **Upgrade database tier** - Production needs dedicated CPU
3. **Implement automated rollback** - Reduce MTTR
4. **Add monitoring alerts** - Proactive issue detection
5. **Secure staging environment** - Add authentication

### Quick Wins

1. Set budget alerts ($100 staging, $500 production)
2. Enable Artifact Registry cleanup policies
3. Add branch constraints to Workload Identity
4. Configure Cloud Run startup CPU boost

### Infrastructure Maturity Roadmap

| Level | Current | Target |
|-------|---------|--------|
| Deployment Automation | ✅ | ✅ |
| Security Scanning | ⚠️ (non-blocking) | ✅ (blocking) |
| Monitoring & Alerting | ❌ | ✅ |
| Auto-Rollback | ❌ | ✅ |
| Multi-Region | ❌ | ⚠️ (optional) |
| Chaos Engineering | ❌ | ⚠️ (optional) |

---

*See [Testing Strategy](./04-testing-strategy.md) for infrastructure testing recommendations.*
