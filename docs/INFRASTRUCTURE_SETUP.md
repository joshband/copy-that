# Infrastructure Setup Guide

Step-by-step guide to set up the complete infrastructure for Copy That from scratch.

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│           GitHub Actions (CI/CD)                │
│  ┌─────────┐  ┌─────────┐  ┌───────────┐      │
│  │ CI/Test │→ │  Build  │→ │  Deploy   │      │
│  └─────────┘  └─────────┘  └───────────┘      │
└──────────────────────┬──────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│         GCP Infrastructure (Terraform)          │
│  ┌───────────────┐         ┌──────────────┐   │
│  │  Cloud Run    │←────────│  Artifact    │   │
│  │  (API)        │         │  Registry    │   │
│  └───────┬───────┘         └──────────────┘   │
│          │                                      │
│          ├──→ ┌──────────────┐                 │
│          │    │  Cloud SQL   │                 │
│          │    │  (Postgres)  │                 │
│          │    └──────────────┘                 │
│          │                                      │
│          └──→ ┌──────────────┐                 │
│               │  Memorystore │                 │
│               │  (Redis)     │                 │
│               └──────────────┘                 │
└─────────────────────────────────────────────────┘
```

## Phase 1: GCP Project Setup (15 minutes)

### Step 1.1: Create GCP Project

```bash
# Set variables
export PROJECT_ID="copy-that-platform"
export REGION="us-central1"
export BILLING_ACCOUNT_ID="YOUR_BILLING_ACCOUNT_ID"

# Create project
gcloud projects create $PROJECT_ID \
  --name="Copy That Platform" \
  --set-as-default

# Link billing account
gcloud billing projects link $PROJECT_ID \
  --billing-account=$BILLING_ACCOUNT_ID

# Verify
gcloud projects describe $PROJECT_ID
```

### Step 1.2: Enable Required APIs

```bash
# Enable all APIs at once
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  vpcaccess.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  --project=$PROJECT_ID

# Verify APIs are enabled
gcloud services list --enabled --project=$PROJECT_ID
```

### Step 1.3: Set Up Terraform State Storage

```bash
# Create GCS bucket
gsutil mb -p $PROJECT_ID -l $REGION \
  gs://${PROJECT_ID}-terraform-state

# Enable versioning for rollback capability
gsutil versioning set on \
  gs://${PROJECT_ID}-terraform-state

# Set lifecycle policy (keep 10 versions)
cat > lifecycle.json <<'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 10,
          "isLive": false
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json \
  gs://${PROJECT_ID}-terraform-state

# Verify
gsutil ls -L gs://${PROJECT_ID}-terraform-state
```

### Step 1.4: Create Service Account for Terraform

```bash
# Create service account
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account" \
  --description="Service account for Terraform" \
  --project=$PROJECT_ID

# Grant necessary roles
for role in \
  roles/editor \
  roles/iam.serviceAccountAdmin \
  roles/resourcemanager.projectIamAdmin \
  roles/serviceusage.serviceUsageAdmin
do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="$role"
done

# Create and download key (store securely!)
gcloud iam service-accounts keys create ~/terraform-sa-key.json \
  --iam-account=terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com

echo "⚠️  Service account key saved to ~/terraform-sa-key.json"
echo "    Keep this file secure and do NOT commit to git!"
```

## Phase 2: Secrets Management (5 minutes)

### Step 2.1: Create API Secrets

```bash
# Anthropic API key
echo -n "YOUR_ANTHROPIC_API_KEY_HERE" | \
  gcloud secrets create anthropic-api-key \
    --replication-policy="automatic" \
    --data-file=- \
    --project=$PROJECT_ID

# OpenAI API key (optional)
echo -n "YOUR_OPENAI_API_KEY_HERE" | \
  gcloud secrets create openai-api-key \
    --replication-policy="automatic" \
    --data-file=- \
    --project=$PROJECT_ID

# Verify secrets
gcloud secrets list --project=$PROJECT_ID
```

### Step 2.2: Generate Application Secrets

```bash
# Generate a secure secret key for the application
python3 -c "import secrets; print(secrets.token_urlsafe(32))" | \
  gcloud secrets create app-secret-key \
    --replication-policy="automatic" \
    --data-file=- \
    --project=$PROJECT_ID

# JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))" | \
  gcloud secrets create jwt-secret \
    --replication-policy="automatic" \
    --data-file=- \
    --project=$PROJECT_ID
```

## Phase 3: Terraform Infrastructure (20 minutes)

### Step 3.1: Configure Terraform

```bash
# Clone repository (if not already done)
git clone https://github.com/joshband/copy-that.git
cd copy-that/deploy/terraform

# Set up authentication
export GOOGLE_APPLICATION_CREDENTIALS=~/terraform-sa-key.json

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
# Project Configuration
project_id        = "${PROJECT_ID}"
region            = "${REGION}"
zone              = "${REGION}-a"
environment       = "staging"
github_repository = "joshband/copy-that"

# Networking
vpc_cidr         = "10.0.0.0/16"
private_ip_range = "10.1.0.0/16"

# Cloud Run Configuration (Staging)
cloudrun_cpu           = "1"
cloudrun_memory        = "512Mi"
cloudrun_max_instances = 10
cloudrun_min_instances = 0
cloudrun_concurrency   = 80

# Database Configuration (Staging)
database_tier           = "db-f1-micro"
database_disk_size      = 10
database_backup_enabled = true
database_ha_enabled     = false

# Redis Configuration (Staging)
redis_tier           = "BASIC"
redis_memory_size_gb = 1

# Artifact Registry
docker_repository_name = "copy-that"

# API Keys (stored in Secret Manager)
anthropic_api_key_secret_name = "anthropic-api-key"
openai_api_key_secret_name    = "openai-api-key"

# Monitoring
enable_monitoring  = true
log_retention_days = 30

# Labels
labels = {
  project     = "copy-that"
  managed_by  = "terraform"
  environment = "staging"
  cost_center = "engineering"
  team        = "platform"
}
EOF
```

### Step 3.2: Initialize Terraform

```bash
# Initialize Terraform (downloads providers)
terraform init

# Validate configuration
terraform validate

# Format Terraform files
terraform fmt -recursive

# Check for issues
terraform plan
```

### Step 3.3: Apply Infrastructure

```bash
# Create execution plan
terraform plan -out=tfplan

# Review the plan carefully
# Look for:
# - Resources to be created
# - Any warnings or errors
# - Estimated costs

# Apply the plan
terraform apply tfplan

# This will take 10-15 minutes
# ⏳ Grab a coffee!
```

### Step 3.4: Verify Infrastructure

```bash
# Check all outputs
terraform output

# Save important values
export ARTIFACT_REGISTRY=$(terraform output -raw artifact_registry_url)
export API_URL=$(terraform output -raw cloudrun_url)
export DB_CONNECTION=$(terraform output -raw database_connection_name)
export WORKLOAD_IDENTITY=$(terraform output -raw workload_identity_provider_name)
export SA_EMAIL=$(terraform output -raw cloudbuild_service_account_email)

# Print summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Infrastructure Provisioned Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Artifact Registry: $ARTIFACT_REGISTRY"
echo "API URL: $API_URL"
echo "Database: $DB_CONNECTION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

## Phase 4: GitHub Actions Setup (10 minutes)

### Step 4.1: Configure GitHub Secrets

```bash
# Get Workload Identity Provider
WORKLOAD_IDENTITY=$(terraform output -raw workload_identity_provider_name)

# Get Service Account Email
SA_EMAIL=$(terraform output -raw cloudbuild_service_account_email)

# Print values to add to GitHub
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Add these to GitHub Secrets:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "GCP_PROJECT_ID: $PROJECT_ID"
echo "GCP_WORKLOAD_IDENTITY_PROVIDER: $WORKLOAD_IDENTITY"
echo "GCP_SERVICE_ACCOUNT: $SA_EMAIL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

### Step 4.2: Add Secrets to GitHub

**Option A: Using GitHub CLI**
```bash
gh secret set GCP_PROJECT_ID -b"$PROJECT_ID"
gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER -b"$WORKLOAD_IDENTITY"
gh secret set GCP_SERVICE_ACCOUNT -b"$SA_EMAIL"

# Verify
gh secret list
```

**Option B: Using GitHub Web UI**
1. Go to `https://github.com/joshband/copy-that/settings/secrets/actions`
2. Click "New repository secret"
3. Add each secret with the values from above

### Step 4.3: Verify Workflows

```bash
# Check workflow files exist
ls -la .github/workflows/

# Expected files:
# - ci.yml (test, lint, type check)
# - build.yml (build and push Docker images)
# - deploy.yml (deploy to Cloud Run)

# View workflow content
cat .github/workflows/ci.yml
```

## Phase 5: Initial Deployment (15 minutes)

### Step 5.1: Build Initial Docker Image

```bash
# Authenticate Docker to Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build image
docker build \
  -f Dockerfile.cloudrun \
  -t copy-that-api:latest \
  .

# Tag for registry
docker tag copy-that-api:latest \
  ${ARTIFACT_REGISTRY}/copy-that-api:latest

# Push to registry
docker push ${ARTIFACT_REGISTRY}/copy-that-api:latest

# Verify
gcloud artifacts docker images list \
  ${REGION}-docker.pkg.dev/${PROJECT_ID}/copy-that
```

### Step 5.2: Run Database Migrations

```bash
# Execute migration job
gcloud run jobs execute copy-that-migrations-staging \
  --region $REGION \
  --wait

# Check execution status
gcloud run jobs executions list \
  --job copy-that-migrations-staging \
  --region $REGION \
  --limit 1

# Check logs if needed
gcloud run jobs executions describe EXECUTION_ID \
  --job copy-that-migrations-staging \
  --region $REGION \
  --format="value(log_uri)"
```

### Step 5.3: Deploy Cloud Run Service

```bash
# Service should already be deployed by Terraform
# Update with latest image
gcloud run services update copy-that-api-staging \
  --image ${ARTIFACT_REGISTRY}/copy-that-api:latest \
  --region $REGION

# Get service URL
export SERVICE_URL=$(gcloud run services describe copy-that-api-staging \
  --region $REGION \
  --format='value(status.url)')

echo "Service deployed at: $SERVICE_URL"
```

### Step 5.4: Verify Deployment

```bash
# Test health endpoint
curl $SERVICE_URL/health

# Expected output:
# {"status":"healthy","version":"0.1.0"}

# Test API docs
open $SERVICE_URL/docs

# Test a basic API endpoint
curl $SERVICE_URL/api/v1/health
```

## Phase 6: Post-Deployment Validation (10 minutes)

### Step 6.1: Smoke Tests

```bash
# Run comprehensive health checks
./scripts/smoke-test.sh $SERVICE_URL

# Or manually:
# Health check
curl -f $SERVICE_URL/health || echo "Health check failed"

# API check
curl -f $SERVICE_URL/api/v1/ || echo "API check failed"

# Database check (returns 200 if DB is accessible)
curl -f $SERVICE_URL/api/v1/health/db || echo "DB check failed"

# Redis check
curl -f $SERVICE_URL/api/v1/health/redis || echo "Redis check failed"
```

### Step 6.2: Check Logs

```bash
# View application logs
gcloud run services logs read copy-that-api-staging \
  --region $REGION \
  --limit 50

# Stream logs
gcloud run services logs tail copy-that-api-staging \
  --region $REGION

# Filter for errors
gcloud run services logs read copy-that-api-staging \
  --region $REGION \
  --log-filter='severity>=ERROR' \
  --limit 20
```

### Step 6.3: Monitor Metrics

```bash
# View in Cloud Console
open "https://console.cloud.google.com/run/detail/${REGION}/copy-that-api-staging/metrics?project=${PROJECT_ID}"

# Check service status via CLI
gcloud run services describe copy-that-api-staging \
  --region $REGION \
  --format='table(status.conditions.type,status.conditions.status,status.conditions.reason)'
```

### Step 6.4: Test CI/CD Pipeline

```bash
# Create a test branch
git checkout -b test-cicd

# Make a small change
echo "# CI/CD Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin test-cicd

# Create pull request
gh pr create \
  --title "Test CI/CD pipeline" \
  --body "Testing automated deployment"

# Watch CI workflow
gh run watch

# After CI passes, merge to develop
gh pr merge --merge

# Watch build and deploy workflows
gh run watch
```

## Phase 7: Production Setup (20 minutes)

### Step 7.1: Create Production Terraform Workspace

```bash
cd deploy/terraform

# Create production workspace
terraform workspace new production
terraform workspace select production

# Create production tfvars
cp terraform.tfvars terraform.tfvars.production
```

### Step 7.2: Update Production Configuration

Edit `terraform.tfvars.production`:

```hcl
environment = "production"

# Higher resources for production
cloudrun_cpu           = "2"
cloudrun_memory        = "1Gi"
cloudrun_max_instances = 100
cloudrun_min_instances = 1
cloudrun_concurrency   = 80

# High-availability database
database_tier           = "db-custom-2-7680"
database_disk_size      = 100
database_backup_enabled = true
database_ha_enabled     = true

# High-availability Redis
redis_tier           = "STANDARD_HA"
redis_memory_size_gb = 5

labels = {
  project     = "copy-that"
  managed_by  = "terraform"
  environment = "production"
  cost_center = "engineering"
  team        = "platform"
}
```

### Step 7.3: Apply Production Infrastructure

```bash
# Plan production infrastructure
terraform plan -var-file=terraform.tfvars.production -out=tfplan.prod

# Review carefully (production changes!)
terraform show tfplan.prod

# Apply
terraform apply tfplan.prod
```

### Step 7.4: Deploy to Production

```bash
# Merge develop to main (triggers production deployment)
git checkout main
git pull origin main
git merge develop
git push origin main

# Monitor deployment
gh run watch

# Verify production deployment
export PROD_URL=$(terraform output -raw cloudrun_url)
curl $PROD_URL/health
```

## Troubleshooting

### Issue: Terraform Apply Fails

**Check:**
1. API enablement: `gcloud services list --enabled`
2. IAM permissions: `gcloud projects get-iam-policy $PROJECT_ID`
3. Quota limits: `gcloud compute project-info describe`

**Fix:**
```bash
# Re-enable APIs
gcloud services enable <service>.googleapis.com

# Request quota increase via Console
open "https://console.cloud.google.com/iam-admin/quotas?project=$PROJECT_ID"
```

### Issue: Docker Push Fails

**Check:**
```bash
# Verify authentication
gcloud auth list
gcloud auth application-default print-access-token

# Re-authenticate
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### Issue: Cloud Run Service Not Responding

**Check:**
```bash
# View logs
gcloud run services logs read copy-that-api-staging \
  --region $REGION \
  --limit 50

# Check service status
gcloud run services describe copy-that-api-staging \
  --region $REGION
```

## Cost Estimates

### Staging Environment

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Cloud Run | 1 CPU, 512Mi, 0-10 instances | $10-30 |
| Cloud SQL | db-f1-micro | $7-15 |
| Redis | BASIC, 1GB | $5-10 |
| Artifact Registry | <100GB | $2-5 |
| Networking | VPC, NAT | $5-10 |
| **Total** | | **$30-70/mo** |

### Production Environment

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Cloud Run | 2 CPU, 1Gi, 1-100 instances | $100-500 |
| Cloud SQL | db-custom-2-7680 HA | $150-250 |
| Redis | STANDARD_HA, 5GB | $50-100 |
| Artifact Registry | <500GB | $10-20 |
| Networking | VPC, NAT | $10-20 |
| **Total** | | **$320-890/mo** |

## Next Steps

1. **Set up monitoring alerts** - Cloud Monitoring
2. **Configure custom domain** - Cloud Run domain mapping
3. **Enable CDN** - Cloud CDN for frontend assets
4. **Set up backups** - Automated database backups
5. **Security hardening** - Implement security best practices
6. **Load testing** - Test at scale with realistic traffic
7. **Disaster recovery** - Document and test recovery procedures

## Support

- **GCP Console**: https://console.cloud.google.com
- **Terraform Registry**: https://registry.terraform.io/providers/hashicorp/google
- **GitHub Actions**: https://docs.github.com/en/actions
- **Project Issues**: https://github.com/joshband/copy-that/issues

---

**Setup Complete!** 🎉

Your infrastructure is now fully provisioned and ready for development and production use.

**Last Updated**: 2025-11-19
