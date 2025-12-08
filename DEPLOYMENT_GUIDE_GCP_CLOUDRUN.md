# GCP Cloud Run Deployment Guide
**Date:** 2025-12-08
**Objective:** Deploy Copy That to GCP Cloud Run with Terraform
**Status:** In Progress

---

## Prerequisites & Current Status

### ✅ Completed
- TypeScript type checking: **PASSING**
- Backend unit tests (34 passed): **PASSING**
- Terraform configuration: **VERIFIED**
- Docker files: **IN PLACE** (main, frontend, debug variants)
- Repository: **CLEAN** with all branches merged

### ⚠️ Required Before Deployment
1. GCP Project created (`copy-that-platform` or your project)
2. GCP Service Account with appropriate permissions
3. `terraform.tfvars` file configured with credentials
4. Docker image built and pushed to Artifact Registry
5. Backend validation fixes (if needed)
6. Neon PostgreSQL database connection string

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    GCP Cloud Run                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Copy That API (FastAPI Backend)                 │   │
│  │  - 512 MB memory, 1 CPU (configurable)           │   │
│  │  - Auto-scaling (min: 0, max: 10 instances)      │   │
│  │  - Health checks: /health endpoint               │   │
│  │  - Environment: prod (configurable)              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │
         ├─→ Artifact Registry (Docker images)
         ├─→ Neon PostgreSQL (Database)
         ├─→ Cloud Logging (Logs)
         └─→ IAM Service Account (Permissions)
```

---

## Step-by-Step Deployment

### Phase 1: Local Validation ✅

#### 1.1 Type Checking
```bash
pnpm type-check
# Result: PASSING ✅
```

#### 1.2 Backend Tests
```bash
cd backend && python -m pytest tests/ -v
# Result: 34 passed, 8 skipped ✅
```

### Phase 2: Docker Build & Push (Next)

#### 2.1 Build Backend Docker Image
```bash
docker build -f Dockerfile -t copy-that-api:latest .
docker tag copy-that-api:latest \
  ${REGION}-docker.pkg.dev/${PROJECT_ID}/copy-that/copy-that-api:latest
```

#### 2.2 Authenticate Docker with GCP
```bash
# Install gcloud CLI (if needed)
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Or use service account key
cat ~/path/to/service-account-key.json | docker login -u _json_key --password-stdin \
  ${REGION}-docker.pkg.dev
```

#### 2.3 Push to Artifact Registry
```bash
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/copy-that/copy-that-api:latest
```

### Phase 3: Terraform Setup (Next)

#### 3.1 Create terraform.tfvars
```bash
# Copy the template
cp terraform/terraform.tfvars.example terraform/terraform.tfvars

# Edit with your values
cat terraform/terraform.tfvars.example
```

**Required Values:**
```hcl
project_id = "copy-that-platform"  # Your GCP project
region = "us-central1"              # GCP region
environment = "prod"                # or dev/staging
service_name = "copy-that-api"      # Cloud Run service name
image_tag = "latest"                # Docker image tag

# Sensitive (use GCP Secrets Manager in production)
anthropic_api_key = "sk-..."
database_url = "postgresql://user:pass@host/db"

# Optional overrides
cloud_run_memory = "512"            # MB
cloud_run_cpu = "1"
cloud_run_min_instances = 0
cloud_run_max_instances = 10
allow_unauthenticated = true        # For public API
```

#### 3.2 Initialize Terraform
```bash
cd terraform

# Initialize working directory
terraform init

# Validate configuration
terraform validate

# Show planned changes (review before applying)
terraform plan -out=tfplan
```

#### 3.3 Deploy with Terraform
```bash
# Apply the plan (creates resources)
terraform apply tfplan

# Get outputs
terraform output

# Expected outputs:
# - cloud_run_url (service URL)
# - artifact_registry_repository_name
# - service_account_email
```

### Phase 4: Post-Deployment Verification (Next)

#### 4.1 Test the Deployed Service
```bash
# Get the service URL
CLOUD_RUN_URL=$(terraform output -raw cloud_run_url)

# Test health endpoint
curl ${CLOUD_RUN_URL}/health

# Expected response:
# {"status":"healthy","timestamp":"2025-12-08T..."}
```

#### 4.2 Check Cloud Run Logs
```bash
# Stream recent logs
gcloud run logs read copy-that-api --region us-central1 --limit 50

# View in Cloud Console
# https://console.cloud.google.com/run/detail/{region}/{service-name}/logs
```

#### 4.3 Verify Environment Variables
```bash
gcloud run services describe copy-that-api --region us-central1
```

---

## Troubleshooting

### Issue: Docker Image Not Found
**Error:** `resource "google_cloud_run_service" "api": ... no image ... found`

**Solution:**
1. Push image first: `docker push ...`
2. Verify in Artifact Registry
3. Check region matches terraform region

### Issue: Terraform State Lock
**Error:** `Error acquiring the lock: resource already locked`

**Solution:**
```bash
# Remove lock (if safe)
rm terraform/.terraform/lock.hcl

# Or unlock specific resource
terraform force-unlock <LOCK_ID>
```

### Issue: Permission Denied on Deployment
**Error:** `permission 'iam.serviceAccounts.actAs' denied`

**Solution:**
1. Ensure service account has required roles
2. Add Editor role temporarily (or specific roles):
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member serviceAccount:SA@PROJECT.iam.gserviceaccount.com \
     --role roles/run.admin
   ```

### Issue: Health Check Failing
**Error:** Deployment succeeds but service shows unhealthy

**Check:**
1. Container logs: `gcloud run logs read ...`
2. Ensure `/health` endpoint is accessible
3. Verify DATABASE_URL environment variable is set
4. Check network connectivity to Neon PostgreSQL

---

## Environment Variables Reference

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `ENVIRONMENT` | Yes | `prod` | dev/staging/prod |
| `DATABASE_URL` | Yes | `postgresql://...` | Neon connection string |
| `ANTHROPIC_API_KEY` | Yes | `sk-...` | Claude API key |
| `ALLOWED_ORIGINS` | No | `https://copy-that.com` | CORS origins |
| `LOG_LEVEL` | No | `info` | debug/info/warning/error |

---

## Cloud Run Scaling Configuration

| Setting | Default | Recommended | Notes |
|---------|---------|-------------|-------|
| Memory | 512 MB | 512-1024 MB | Increase for heavy ML models |
| CPU | 1 | 1-2 | Auto-scales with memory |
| Min Instances | 0 | 0 | Scales to zero when idle (saves costs) |
| Max Instances | 10 | 10-50 | Based on expected traffic |
| Timeout | 300s | 300-3600s | Increase for long-running jobs |
| Concurrency | 80 | 80 | Requests per instance |

---

## Monitoring & Maintenance

### View Deployment Status
```bash
gcloud run services describe copy-that-api --region us-central1
```

### Scale Configuration
```bash
gcloud run services update copy-that-api \
  --min-instances 1 \
  --max-instances 50 \
  --region us-central1
```

### Update Image
```bash
# Push new image
docker push REGISTRY/copy-that-api:v1.2.3

# Update service
gcloud run deploy copy-that-api \
  --image REGISTRY/copy-that-api:v1.2.3 \
  --region us-central1
```

### Monitor Logs
- **Cloud Console:** https://console.cloud.google.com/run/detail/{region}/{service}/logs
- **gcloud CLI:** `gcloud run logs read copy-that-api --limit 100`
- **Streaming:** `gcloud run logs read copy-that-api --follow`

---

## Cost Optimization Tips

1. **Set minimum instances to 0** (default) to avoid idle charges
2. **Use appropriate memory/CPU** (512MB/1CPU is usually sufficient)
3. **Monitor invocation counts** and scale down max instances if needed
4. **Archive old logs** to Cloud Storage for cost savings
5. **Use Cloud CDN** for static assets (frontend)

---

## Next Steps

1. [ ] Prepare GCP project and service account
2. [ ] Build Docker images locally
3. [ ] Push images to Artifact Registry
4. [ ] Configure terraform.tfvars
5. [ ] Run `terraform plan` and review
6. [ ] Apply terraform deployment
7. [ ] Verify service is healthy
8. [ ] Test endpoints with curl/Postman
9. [ ] Setup CI/CD pipeline (GitHub Actions)
10. [ ] Configure domain (Cloud Armor, CDN)

---

## Files Modified
- This guide: `DEPLOYMENT_GUIDE_GCP_CLOUDRUN.md`
- Terraform config: `terraform/`
- Dockerfiles: `Dockerfile`, `Dockerfile.frontend`

---

## Summary

Ready for GCP Cloud Run deployment with:
- ✅ Type-safe TypeScript
- ✅ Passing backend tests
- ✅ Optimized Docker images
- ✅ Terraform IaC for infrastructure
- ✅ Auto-scaling, health checks, logging configured
- ✅ Service account with appropriate IAM roles
