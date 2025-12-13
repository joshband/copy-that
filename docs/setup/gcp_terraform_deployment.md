# GCP Deployment with Terraform

Deploy Copy That to Google Cloud Platform using Infrastructure as Code (Terraform).

**Cost:** $0/month (free tier) for hobbyist use ✅

---

## Architecture

```
┌─────────────────────────────────────────┐
│  Neon PostgreSQL (FREE)                 │
│  (Existing database, no changes needed) │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Cloud Run (FREE - 2M requests/month)   │
│  ├─ Docker image deployment             │
│  ├─ Auto-scaling (0-10 instances)       │
│  └─ Health checks + monitoring          │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Artifact Registry (FREE tier)          │
│  └─ Stores Docker images                │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Vercel Frontend (FREE)                 │
│  (Deployed separately)                  │
└─────────────────────────────────────────┘
```

---

## Prerequisites

### 1. GCP Account Setup

- ✅ GCP Project: `copy-that-platform` (already created)
- ✅ Billing account: Linked to project (for tracking, no charges for free tier)

### 2. Install Required Tools

```bash
# Install Terraform
brew install terraform

# Install Google Cloud SDK
brew install --cask google-cloud-sdk

# Install Docker
brew install docker
```

### 3. Authenticate with GCP

```bash
# Login to GCP
gcloud auth login

# Set your default project
gcloud config set project copy-that-platform

# Create application default credentials (for Terraform)
gcloud auth application-default login
```

### 4. Get Required Secrets

Before deployment, gather:

1. **Neon Database URL**
   - Go to: https://console.neon.tech
   - Copy connection string: `postgresql://user:password@host.neon.tech/dbname?sslmode=require`

2. **Anthropic API Key**
   - Go to: https://console.anthropic.com
   - Create/copy API key: `sk-proj-...`

---

## Deployment Steps

### Step 1: Prepare Terraform Configuration

```bash
cd deploy/terraform/

# Copy example to actual config
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
vim terraform.tfvars  # Or open in your editor
```

**Fill in `terraform.tfvars`:**

```hcl
project_id = "copy-that-platform"
region     = "us-central1"
environment = "prod"

# Database URL from Neon
database_url = "postgresql://..."

# API key from Anthropic
anthropic_api_key = "sk-proj-..."
```

⚠️ **IMPORTANT**: Never commit `terraform.tfvars` to git!

```bash
# Already in .gitignore, but verify
echo "terraform.tfvars" >> ../.gitignore
```

### Step 2: Initialize Terraform

```bash
terraform init
```

This downloads the Google Cloud provider plugin (~50MB).

### Step 3: Plan Infrastructure

```bash
terraform plan -out=tfplan
```

Review the output. You should see:
- 1x Artifact Registry repository
- 1x Cloud Run service
- 1x Service account
- API enablements (Cloud Run, Artifact Registry, etc.)

### Step 4: Apply Infrastructure

```bash
terraform apply tfplan
```

This creates:
- Artifact Registry repository: `us-central1-docker.pkg.dev/copy-that-platform/copy-that/`
- Cloud Run service: `copy-that-api` (with auto-scaling 0-10 instances)
- Service account: `copy-that-api-sa@copy-that-platform.iam.gserviceaccount.com`

**Expected output:**
```
Outputs:

artifact_registry_image_path = "us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:latest"
cloud_run_service_url = "https://copy-that-api-xyz.a.run.app"
service_account_email = "copy-that-api-sa@copy-that-platform.iam.gserviceaccount.com"
```

**Save these URLs** - you'll need them next.

### Step 5: Build & Push Docker Image

```bash
# Navigate to project root
cd ..

# Set variables for convenience
PROJECT_ID="copy-that-platform"
REGION="us-central1"
SERVICE_NAME="copy-that-api"
IMAGE_TAG="latest"
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/copy-that/${SERVICE_NAME}:${IMAGE_TAG}"

# Configure Docker authentication with GCP
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build Docker image (uses Dockerfile with production target)
docker build -t ${IMAGE_PATH} --target production .

# Push to Artifact Registry
docker push ${IMAGE_PATH}

# Verify image was pushed
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/copy-that
```

### Step 6: Deploy to Cloud Run

```bash
# Option A: Update Terraform and reapply (recommended)
cd deploy/terraform/
terraform apply
cd ..

# Option B: Manual deployment
gcloud run deploy copy-that-api \
  --image ${IMAGE_PATH} \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=postgresql://...,ANTHROPIC_API_KEY=sk-proj-...
```

### Step 7: Verify Deployment

```bash
# Get Cloud Run service URL
CLOUD_RUN_URL=$(terraform -chdir=terraform output -raw cloud_run_service_url)

# Test health endpoint
curl ${CLOUD_RUN_URL}/health

# Expected response:
# {"status":"ok","version":"0.1.0"}
```

### Step 8: View Logs

```bash
# View recent logs (last 50 lines)
gcloud run logs read copy-that-api --region=us-central1 --limit=50

# Stream live logs
gcloud run logs read copy-that-api --region=us-central1 --follow
```

---

## Configuration Reference

### Cloud Run Resource Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| Memory | 512 MB | Good for Python + FastAPI |
| CPU | 1 | Scales with memory |
| Timeout | 300s (5 min) | For image processing |
| Min instances | 0 | Scales to zero (saves cost) |
| Max instances | 10 | Prevents runaway costs |
| Concurrency | 80 | Requests per instance |

### Environment Variables

Configured automatically from `terraform.tfvars`:

```
ENVIRONMENT=prod
DATABASE_URL=postgresql://...
ANTHROPIC_API_KEY=sk-proj-...
ALLOWED_ORIGINS=https://copy-that.com
LOG_LEVEL=info
```

### Health Checks

Cloud Run automatically checks `/health` endpoint:
- Startup check: Every 10 seconds (max 3 failures)
- Liveness check: Every 30 seconds (max 3 failures)

If health checks fail, instance is restarted automatically.

---

## Monitoring

### View Logs

```bash
# Cloud Run logs (from service)
gcloud run logs read copy-that-api --region=us-central1

# Cloud Logging (with filters)
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=copy-that-api"
```

### View Metrics

Open Google Cloud Console:
- https://console.cloud.google.com/run/detail/us-central1/copy-that-api?project=copy-that-platform

Watch:
- **Requests**: Should be ~0 (no traffic yet)
- **Errors**: Should be 0%
- **Latency**: Average response time
- **Memory**: Should be < 512MB

### Alerts (Optional)

```bash
# Create alert for error rate > 5%
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="Copy That Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

---

## Scaling & Performance

### Auto-Scaling

Cloud Run automatically scales based on:
- **CPU utilization**
- **Concurrent requests**
- **Min/max instance limits**

Current configuration:
- **Min**: 0 instances (scale to zero when idle, FREE)
- **Max**: 10 instances (prevents runaway costs)

### Cost Estimation

| Metric | Free Tier | Hobby | Production |
|--------|-----------|-------|------------|
| **Requests/month** | 2M | 100K-500K | 1M+ |
| **Compute time** | 360K GB-s | ~1K GB-s | ~10K GB-s |
| **Cost** | $0 | $0 | ~$10-50 |

Your hobby usage should stay in free tier indefinitely.

---

## Updating Deployment

### Update Code & Redeploy

```bash
# 1. Make code changes
# 2. Commit to git
git add .
git commit -m "feat: new feature"

# 3. Build new Docker image
docker build -t us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:v1.0.0 --target production .

# 4. Push to Artifact Registry
docker push us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:v1.0.0

# 5. Update image tag in terraform.tfvars
# image_tag = "v1.0.0"

# 6. Reapply Terraform
cd deploy/terraform/
terraform apply
```

### Rollback

```bash
# Redeploy previous image
docker push us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:previous-tag

# Update terraform.tfvars
# image_tag = "previous-tag"

# Reapply
terraform apply
```

---

## Troubleshooting

### Issue: Cloud Run service not responding

**Causes:**
- Health checks failing (wrong `/health` endpoint)
- Database connection error (wrong DATABASE_URL)
- Missing API key (check ANTHROPIC_API_KEY)

**Debug:**
```bash
# View logs
gcloud run logs read copy-that-api --region=us-central1 --limit=100

# Check deployment status
gcloud run services describe copy-that-api --region=us-central1

# Test locally first
docker run -e DATABASE_URL=postgresql://... \
  -e ANTHROPIC_API_KEY=sk-proj-... \
  us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:latest
```

### Issue: Docker image build fails

**Solution:**
```bash
# Check Dockerfile syntax
docker build --target production .

# Check dependencies in pyproject.toml
python -m pip install -e ".[dev]"

# Run tests before building
pnpm test
python -m pytest tests/
```

### Issue: Permission denied pushing to Artifact Registry

**Solution:**
```bash
# Reconfigure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Verify credentials
gcloud auth list
```

### Issue: Cloud Run complaining about CORS

**Solution:**
Update `allowed_origins` in `terraform.tfvars`:

```hcl
allowed_origins = "https://yourfrontend.com,https://www.yourfrontend.com"
```

Then reapply:
```bash
cd deploy/terraform/
terraform apply
```

---

## Cleanup

### Remove All Resources

⚠️ This will delete everything:

```bash
cd deploy/terraform/

# View what will be deleted
terraform plan -destroy

# Delete all resources
terraform destroy
```

### Partial Cleanup

To delete specific resources:

```bash
# Delete Cloud Run service only
terraform destroy -target=google_cloud_run_service.api

# Delete Artifact Registry only
terraform destroy -target=google_artifact_registry_repository.docker_repo
```

---

## Security Considerations

### API Keys & Secrets

- ✅ Terraform: Uses Google Secret Manager (recommended)
- ✅ Environment variables: Stored in Cloud Run (encrypted)
- ❌ terraform.tfvars: Never commit to git (already in .gitignore)

### Network Security

- ✅ Cloud Run: HTTPS/TLS by default
- ✅ Service account: Limited permissions (logging only)
- ❌ Public access: Enabled by default (adjust if needed)

To restrict access:
```hcl
allow_unauthenticated = false  # Requires authentication
```

### Database Security

- ✅ Neon: SSL/TLS enabled
- ✅ PASSWORD: Environment variable (not in code)
- ✅ IP allowlist: Neon's free tier doesn't restrict IPs

---

## Next Steps

### 1. Connect Frontend

After deployment, update frontend `.env.production`:

```env
VITE_API_URL=https://copy-that-api-xyz.a.run.app/api/v1
VITE_ENVIRONMENT=production
```

Deploy to Vercel:
```bash
vercel deploy --prod
```

### 2. Setup Custom Domain (Optional)

If you have a domain:

```bash
# Create Cloud Load Balancer
# Point domain to Cloud Run URL
# Setup SSL certificate (automatic)

# Or use Cloud CDN for caching
```

### 3. Monitoring & Alerts

```bash
# View all metrics
gcloud monitoring dashboards create --config-from-file=monitoring-config.yaml

# Setup email alerts
gcloud alpha monitoring policies create ...
```

### 4. CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker image
        run: |
          gcloud auth configure-docker us-central1-docker.pkg.dev
          docker build -t us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:latest .
          docker push us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:latest

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy copy-that-api ...
```

---

## Support Resources

- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/google
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Artifact Registry Docs**: https://cloud.google.com/artifact-registry/docs
- **GCP CLI Reference**: https://cloud.google.com/sdk/gcloud/reference

---

**Version**: 1.0.0
**Last Updated**: 2025-11-20
**Status**: Ready for Deployment ✅
