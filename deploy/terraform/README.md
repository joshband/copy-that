# Terraform Infrastructure for Copy That

This directory contains Terraform configurations to provision and manage the GCP infrastructure for Copy That.

## Overview

The infrastructure includes:
- **Cloud Run**: Serverless container deployment for the API
- **Cloud SQL**: PostgreSQL 16 database
- **Memorystore**: Redis cache
- **Artifact Registry**: Docker image storage
- **VPC**: Private networking with Cloud NAT
- **Secret Manager**: Secure credential storage
- **IAM**: Service accounts and Workload Identity for GitHub Actions

## Prerequisites

1. **GCP Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Terraform** >= 1.5 installed
4. **Appropriate IAM permissions** (Owner or Editor role)

## Quick Start

### 1. Authenticate with GCP

```bash
gcloud auth application-default login
gcloud config set project copy-that-platform
```

### 2. Create GCS Bucket for Terraform State

```bash
gsutil mb -p copy-that-platform -l us-central1 gs://copy-that-terraform-state
gsutil versioning set on gs://copy-that-terraform-state
```

### 3. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
vim terraform.tfvars
```

Required variables:
- `project_id`: Your GCP project ID
- `region`: GCP region (default: us-central1)
- `environment`: staging or production
- `github_repository`: Your GitHub repo (owner/name)

### 4. Initialize Terraform

```bash
terraform init
```

### 5. Plan the Infrastructure

```bash
# Review what will be created
terraform plan -out=tfplan

# For specific environment
terraform plan -var="environment=staging" -out=tfplan
```

### 6. Apply the Configuration

```bash
terraform apply tfplan
```

This will take 10-15 minutes to provision all resources.

## Configuration Files

| File | Purpose |
|------|---------|
| `main.tf` | Main configuration, provider setup, service accounts |
| `variables.tf` | Input variables and defaults |
| `outputs.tf` | Output values after apply |
| `networking.tf` | VPC, subnets, Cloud NAT, VPC connector |
| `artifact_registry.tf` | Docker image repository |
| `cloudsql.tf` | PostgreSQL database configuration |
| `redis.tf` | Redis (Memorystore) configuration |
| `cloudrun.tf` | Cloud Run services and jobs |
| `terraform.tfvars` | Your variable values (gitignored) |

## Resource Overview

### Staging Environment

**Compute:**
- Cloud Run: 0-10 instances, 1 CPU, 512Mi RAM
- Estimated cost: ~$10-30/month

**Database:**
- Cloud SQL: db-f1-micro (shared CPU)
- Redis: BASIC tier, 1GB
- Estimated cost: ~$15-25/month

**Total Staging Cost: ~$25-55/month**

### Production Environment

**Compute:**
- Cloud Run: 1-100 instances, 2 CPU, 1Gi RAM
- Estimated cost: ~$100-500/month (usage-based)

**Database:**
- Cloud SQL: db-custom-2-7680 (2 vCPU, 7.5GB RAM) with HA
- Redis: STANDARD_HA tier, 5GB
- Estimated cost: ~$150-250/month

**Total Production Cost: ~$250-750/month**

## Environments

### Staging

```bash
terraform workspace new staging
terraform workspace select staging
terraform apply -var="environment=staging"
```

### Production

```bash
terraform workspace new production
terraform workspace select production
terraform apply -var="environment=production"
```

## Managing Infrastructure

### View Current State

```bash
terraform show
terraform state list
```

### Update Single Resource

```bash
# Example: Update Cloud Run service
terraform apply -target=google_cloud_run_v2_service.api
```

### Import Existing Resources

```bash
# Example: Import existing Cloud SQL instance
terraform import google_sql_database_instance.postgres copy-that-postgres-staging
```

### Destroy Infrastructure

```bash
# ⚠️ DANGEROUS: Destroys all resources
terraform destroy -var="environment=staging"

# Destroy specific resource
terraform destroy -target=google_cloud_run_v2_service.api
```

## Outputs

After applying, you'll see:

```bash
terraform output
```

Important outputs:
- `api_url`: Your Cloud Run service URL
- `database_connection`: Cloud SQL connection name
- `docker_repository`: Full path to push Docker images
- `workload_identity_provider_name`: For GitHub Actions

### Use Outputs in Scripts

```bash
# Get specific output
API_URL=$(terraform output -raw api_url)
echo "API deployed at: $API_URL"

# Get all helpful commands
terraform output -json helpful_commands | jq -r '.deploy_cloudrun'
```

## GitHub Actions Integration

The Terraform configuration creates a Workload Identity Pool for GitHub Actions.

### Configure GitHub Secrets

Add these to your GitHub repository secrets:

```bash
# Get the Workload Identity Provider
WORKLOAD_IDENTITY_PROVIDER=$(terraform output -raw workload_identity_provider_name)

# Get service account email
SERVICE_ACCOUNT=$(terraform output -raw cloudbuild_service_account)

echo "Add these to GitHub Secrets:"
echo "GCP_PROJECT_ID: copy-that-platform"
echo "GCP_WORKLOAD_IDENTITY_PROVIDER: $WORKLOAD_IDENTITY_PROVIDER"
echo "GCP_SERVICE_ACCOUNT: $SERVICE_ACCOUNT"
```

## Common Tasks

### Run Database Migrations

```bash
# Via gcloud
gcloud run jobs execute copy-that-migrations-staging \
  --region us-central1 \
  --wait

# Via Terraform output
eval $(terraform output -json helpful_commands | jq -r '.run_migrations')
```

### View Logs

```bash
# Via gcloud
gcloud run services logs read copy-that-api-staging \
  --region us-central1 \
  --limit 50 \
  --format json

# Via Terraform output
eval $(terraform output -json helpful_commands | jq -r '.view_logs')
```

### Connect to Database

```bash
# Via Cloud SQL Proxy
gcloud sql connect copy-that-postgres-staging \
  --database=copy_that

# Or use connection name
terraform output database_connection
```

### Scale Cloud Run Service

```bash
# Update variables.tf or terraform.tfvars
cloudrun_max_instances = 20

# Apply changes
terraform apply -var="cloudrun_max_instances=20"
```

## Security Best Practices

1. **Never commit `terraform.tfvars`** - Contains sensitive data
2. **Use separate workspaces** for staging and production
3. **Enable deletion protection** for production databases
4. **Rotate secrets regularly** via Secret Manager
5. **Review IAM permissions** periodically
6. **Enable audit logging** for compliance
7. **Use least privilege** for service accounts

## Troubleshooting

### Error: API not enabled

```bash
# Enable required APIs manually
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com
```

### Error: Insufficient permissions

```bash
# Check your IAM roles
gcloud projects get-iam-policy copy-that-platform \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:YOUR_EMAIL"

# Grant Owner role (requires org admin)
gcloud projects add-iam-policy-binding copy-that-platform \
  --member="user:YOUR_EMAIL" \
  --role="roles/owner"
```

### Error: State lock

```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

### Error: Resource quota exceeded

```bash
# Check quotas
gcloud compute project-info describe --project=copy-that-platform

# Request quota increase via Console
# https://console.cloud.google.com/iam-admin/quotas
```

## Maintenance

### Update Terraform Version

```bash
# Check current version
terraform version

# Upgrade providers
terraform init -upgrade
```

### Backup State

```bash
# State is already backed up in GCS
# Manual backup
terraform state pull > terraform.tfstate.backup
```

### Clean Up Old State Versions

```bash
# List state versions
gsutil ls -a gs://copy-that-terraform-state/terraform/state/

# Keep last 10 versions, delete older
gsutil -m rm gs://copy-that-terraform-state/**#<generation>
```

## Cost Optimization

1. **Use committed use discounts** for production
2. **Enable autoscaling** with min instances = 0 for staging
3. **Use preemptible VMs** for non-critical workloads
4. **Set up budget alerts** in GCP Console
5. **Review Cloud Run request costs** weekly
6. **Archive old database backups** after 90 days

## Support

- **Terraform Documentation**: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- **GCP Documentation**: https://cloud.google.com/docs
- **Issues**: Open an issue in the GitHub repository

---

**Last Updated**: 2025-11-19
