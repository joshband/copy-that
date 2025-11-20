# Deployment Guide

Complete guide for deploying Copy That to Google Cloud Platform.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Infrastructure Provisioning](#infrastructure-provisioning)
- [CI/CD Configuration](#cicd-configuration)
- [Manual Deployment](#manual-deployment)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

## Overview

Copy That uses a modern cloud-native architecture deployed on GCP:

- **Cloud Run**: Serverless container platform
- **Cloud SQL**: Managed PostgreSQL database
- **Memorystore**: Managed Redis cache
- **Artifact Registry**: Docker image storage
- **Secret Manager**: Secure credential management
- **Terraform**: Infrastructure as Code
- **GitHub Actions**: CI/CD automation

## Prerequisites

### Required Tools

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install Terraform
brew install terraform  # macOS
# or download from https://terraform.io/downloads

# Install Docker
brew install --cask docker  # macOS

# Verify installations
gcloud version
terraform version
docker --version
```

### Required Access

- GCP account with billing enabled
- Owner or Editor role on GCP project
- GitHub repository admin access

## Initial Setup

### 1. Create GCP Project

```bash
# Set project ID
export PROJECT_ID="copy-that-platform"
export REGION="us-central1"

# Create project (if needed)
gcloud projects create $PROJECT_ID \
  --name="Copy That Platform"

# Set as default project
gcloud config set project $PROJECT_ID

# Enable billing
gcloud billing accounts list
gcloud billing projects link $PROJECT_ID \
  --billing-account=ACCOUNT_ID
```

### 2. Enable Required APIs

```bash
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
  cloudscheduler.googleapis.com
```

### 3. Create Terraform State Bucket

```bash
# Create GCS bucket for Terraform state
gsutil mb -p $PROJECT_ID -l $REGION gs://copy-that-terraform-state

# Enable versioning
gsutil versioning set on gs://copy-that-terraform-state

# Set lifecycle policy (optional - keep 10 versions)
cat > lifecycle.json <<EOF
{
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
EOF

gsutil lifecycle set lifecycle.json gs://copy-that-terraform-state
```

### 4. Create API Secrets

```bash
# Create Anthropic API key secret
echo -n "YOUR_ANTHROPIC_API_KEY" | \
  gcloud secrets create anthropic-api-key \
    --data-file=- \
    --replication-policy=automatic

# Create OpenAI API key secret (optional)
echo -n "YOUR_OPENAI_API_KEY" | \
  gcloud secrets create openai-api-key \
    --data-file=- \
    --replication-policy=automatic

# Verify secrets
gcloud secrets list
```

## Infrastructure Provisioning

### 1. Configure Terraform

```bash
cd deploy/terraform

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
vim terraform.tfvars
```

Required variables in `terraform.tfvars`:

```hcl
project_id        = "copy-that-platform"
region            = "us-central1"
environment       = "staging"
github_repository = "joshband/copy-that"

# Staging configuration
cloudrun_cpu           = "1"
cloudrun_memory        = "512Mi"
cloudrun_max_instances = 10
cloudrun_min_instances = 0

database_tier      = "db-f1-micro"
database_disk_size = 10

redis_tier           = "BASIC"
redis_memory_size_gb = 1
```

### 2. Initialize and Apply Terraform

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan changes
terraform plan -out=tfplan

# Review plan carefully, then apply
terraform apply tfplan
```

This will take 10-15 minutes. Terraform will create:
- VPC network and subnets
- VPC Access Connector
- Cloud SQL (PostgreSQL)
- Redis (Memorystore)
- Artifact Registry
- Service accounts
- IAM bindings
- Workload Identity for GitHub Actions

### 3. Save Terraform Outputs

```bash
# View all outputs
terraform output

# Save important values
export ARTIFACT_REGISTRY=$(terraform output -raw docker_repository)
export API_URL=$(terraform output -raw api_url)
export WORKLOAD_IDENTITY_PROVIDER=$(terraform output -raw workload_identity_provider_name)
export SERVICE_ACCOUNT=$(terraform output -raw cloudbuild_service_account)

echo "Artifact Registry: $ARTIFACT_REGISTRY"
echo "API URL: $API_URL"
echo "Workload Identity Provider: $WORKLOAD_IDENTITY_PROVIDER"
echo "Service Account: $SERVICE_ACCOUNT"
```

## CI/CD Configuration

### 1. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `GCP_PROJECT_ID` | `copy-that-platform` | Your project ID |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/...` | `terraform output -raw workload_identity_provider_name` |
| `GCP_SERVICE_ACCOUNT` | `copy-that-cloudbuild@...` | `terraform output -raw cloudbuild_service_account` |

### 2. Verify GitHub Actions Workflows

Check that these workflow files exist:
- `.github/workflows/ci.yml` - Run tests, lint, type check
- `.github/workflows/build.yml` - Build and push Docker images
- `.github/workflows/deploy.yml` - Deploy to Cloud Run

### 3. Test CI/CD Pipeline

```bash
# Create a test branch
git checkout -b test-deployment

# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin test-deployment

# Create PR (triggers CI workflow)
gh pr create --title "Test deployment" --body "Testing CI/CD"

# Merge to develop (triggers build + deploy to staging)
gh pr merge --merge

# Check deployment
gcloud run services list --region us-central1
```

## Manual Deployment

If you need to deploy manually without GitHub Actions:

### 1. Build Docker Image

```bash
# Authenticate Docker to Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build image
docker build -f Dockerfile.cloudrun -t copy-that-api:latest .

# Tag for registry
docker tag copy-that-api:latest \
  us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:latest

# Push to registry
docker push us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:latest
```

### 2. Run Database Migrations

```bash
# Execute migration job
gcloud run jobs execute copy-that-migrations-staging \
  --region us-central1 \
  --wait

# Check migration status
gcloud run jobs executions list \
  --job copy-that-migrations-staging \
  --region us-central1 \
  --limit 1
```

### 3. Deploy to Cloud Run

```bash
# Deploy service
gcloud run deploy copy-that-api-staging \
  --image us-central1-docker.pkg.dev/copy-that-platform/copy-that/copy-that-api:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated

# Get service URL
gcloud run services describe copy-that-api-staging \
  --region us-central1 \
  --format='value(status.url)'
```

## Post-Deployment

### 1. Verify Deployment

```bash
# Get service URL
export API_URL=$(gcloud run services describe copy-that-api-staging \
  --region us-central1 \
  --format='value(status.url)')

# Test health endpoint
curl $API_URL/health

# Test API docs
open $API_URL/docs
```

### 2. Check Logs

```bash
# View recent logs
gcloud run services logs read copy-that-api-staging \
  --region us-central1 \
  --limit 50

# Stream logs
gcloud run services logs tail copy-that-api-staging \
  --region us-central1

# View in Console
open "https://console.cloud.google.com/run/detail/us-central1/copy-that-api-staging/logs"
```

### 3. Monitor Metrics

```bash
# View metrics in Console
open "https://console.cloud.google.com/run/detail/us-central1/copy-that-api-staging/metrics"

# Check service status
gcloud run services describe copy-that-api-staging \
  --region us-central1 \
  --format='table(status.conditions)'
```

### 4. Test Database Connection

```bash
# Connect to Cloud SQL
gcloud sql connect copy-that-postgres-staging \
  --database=copy_that

# Run test query
SELECT version();
\l
\dt
\q
```

### 5. Test Redis Connection

```bash
# Get Redis IP
export REDIS_HOST=$(terraform output -raw redis_host)
export REDIS_PORT=$(terraform output -raw redis_port)

echo "Redis: $REDIS_HOST:$REDIS_PORT"

# Test with telnet (from Cloud Shell or VM in same VPC)
telnet $REDIS_HOST $REDIS_PORT
PING
```

## Troubleshooting

### Deployment Fails

**Check service logs:**
```bash
gcloud run services logs read copy-that-api-staging \
  --region us-central1 \
  --limit 50
```

**Common issues:**
- Database connection: Check VPC connector and Cloud SQL proxy
- Secrets access: Verify IAM permissions for service account
- Container crashes: Check application logs for errors

### Database Connection Issues

**Test Cloud SQL connectivity:**
```bash
# From Cloud Shell
gcloud sql connect copy-that-postgres-staging

# Check Cloud SQL status
gcloud sql instances describe copy-that-postgres-staging \
  --format='value(state)'
```

**Check VPC Access Connector:**
```bash
gcloud compute networks vpc-access connectors describe \
  copy-that-connector-staging \
  --region us-central1
```

### CI/CD Pipeline Fails

**Check GitHub Actions logs:**
1. Go to repository → Actions tab
2. Click on failed workflow run
3. Review job logs

**Common issues:**
- Authentication: Check GitHub secrets configuration
- Image push fails: Verify Artifact Registry permissions
- Deployment timeout: Increase timeout in workflow

### Performance Issues

**Scale up Cloud Run:**
```bash
# Update Terraform variables
vim deploy/terraform/terraform.tfvars

# Increase resources
cloudrun_cpu           = "2"
cloudrun_memory        = "1Gi"
cloudrun_max_instances = 20

# Apply changes
cd deploy/terraform
terraform apply
```

**Scale up database:**
```bash
# Update database tier
database_tier = "db-custom-2-7680"

terraform apply
```

## Rollback

### Rollback Cloud Run Deployment

```bash
# List revisions
gcloud run revisions list \
  --service copy-that-api-staging \
  --region us-central1

# Rollback to previous revision
gcloud run services update-traffic copy-that-api-staging \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

### Rollback Database Migration

```bash
# Connect to database
gcloud sql connect copy-that-postgres-staging --database=copy_that

# Check migration history
SELECT * FROM alembic_version;

# Downgrade (from Cloud Run job or local)
alembic downgrade -1
```

## Production Deployment

### 1. Update Variables for Production

```bash
cd deploy/terraform

# Create production tfvars
cp terraform.tfvars terraform.tfvars.production

# Update for production
vim terraform.tfvars.production
```

Production configuration:
```hcl
environment = "production"

# Higher resources
cloudrun_cpu           = "2"
cloudrun_memory        = "1Gi"
cloudrun_max_instances = 100
cloudrun_min_instances = 1

# HA database
database_tier       = "db-custom-2-7680"
database_ha_enabled = true

# HA Redis
redis_tier           = "STANDARD_HA"
redis_memory_size_gb = 5
```

### 2. Create Production Workspace

```bash
terraform workspace new production
terraform workspace select production

terraform apply -var-file=terraform.tfvars.production
```

### 3. Deploy to Production

Merge `develop` → `main` to trigger production deployment:

```bash
git checkout main
git pull origin main
git merge develop
git push origin main

# Monitor deployment
gh run watch
```

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check service health
- Review usage metrics

**Weekly:**
- Review cost reports
- Update dependencies
- Run security scans

**Monthly:**
- Database backups verification
- Capacity planning
- Security audit

### Backup and Restore

**Manual database backup:**
```bash
gcloud sql export sql copy-that-postgres-staging \
  gs://copy-that-backups/backup-$(date +%Y%m%d).sql \
  --database=copy_that
```

**Restore from backup:**
```bash
gcloud sql import sql copy-that-postgres-staging \
  gs://copy-that-backups/backup-20250119.sql \
  --database=copy_that
```

## Cost Optimization

1. **Use minimum instances = 0** for staging
2. **Enable autoscaling** with appropriate limits
3. **Use committed use discounts** for production
4. **Set up budget alerts**
5. **Review Cloud Run request logs** weekly

## Support

- **GCP Documentation**: https://cloud.google.com/docs
- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/google
- **GitHub Issues**: Report deployment issues

---

**Last Updated**: 2025-11-19
