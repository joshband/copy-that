# Minimal Cost Setup Guide

**Perfect for:** Personal projects, demos, sharing with family/friends

**Cost:** ~$0-5/month (only pay when URL is visited)

## What You Get

- ✅ Public URL to share with anyone
- ✅ Production-quality infrastructure
- ✅ Automatic HTTPS
- ✅ Auto-scaling (0-5 instances)
- ✅ Zero cost when idle
- ✅ Secure enough for personal/demo use

## Architecture Comparison

### Full Setup (main.tf) - $30-70/month
```
Cloud Run → VPC → Cloud SQL (Postgres) ← Always $7-15/mo
                → Memorystore (Redis)  ← Always $5-10/mo
                → Cloud NAT            ← Always $45/mo
```

### Minimal Setup (main-minimal.tf) - $0-5/month
```
Cloud Run → Internet → Neon.tech (Postgres) ← FREE
                    → Upstash (Redis)        ← FREE
```

## Step-by-Step Setup

### Prerequisites

```bash
# Install tools (if not already done)
brew install gcloud terraform gh

# Authenticate
gcloud auth login
gcloud auth application-default login
```

### Step 1: Create Free External Services (10 minutes)

#### 1.1 Neon.tech (PostgreSQL)

```bash
# 1. Sign up: https://neon.tech
# 2. Create new project: "copy-that"
# 3. Copy connection string

# Example connection string:
# postgresql://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Neon Free Tier:**
- 3GB storage
- 100 compute hours/month
- Auto-pause after inactivity
- SSL/TLS encryption
- SOC 2 Type II certified

#### 1.2 Upstash (Redis)

```bash
# 1. Sign up: https://console.upstash.com
# 2. Create new database: "copy-that-cache"
# 3. Copy connection string

# Example connection string:
# redis://default:password@usw2-enabled-firefly-12345.upstash.io:6379
```

**Upstash Free Tier:**
- 10K commands/day
- 256MB storage
- TLS encryption
- Global replication

### Step 2: Set Up GCP Project (5 minutes)

```bash
# Set variables
export PROJECT_ID="copy-that-platform"
export REGION="us-central1"

# Create project (if needed)
gcloud projects create $PROJECT_ID --name="Copy That Platform"
gcloud config set project $PROJECT_ID

# Link billing
gcloud billing projects link $PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT_ID

# Enable APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  cloudbuild.googleapis.com

# Create state bucket
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-terraform-state
gsutil versioning set on gs://${PROJECT_ID}-terraform-state
```

### Step 3: Store Connection Strings in Secrets (2 minutes)

```bash
# Store Neon database URL
echo "postgresql://YOUR_NEON_CONNECTION_STRING" | \
  gcloud secrets create database-url-external \
    --replication-policy="automatic" \
    --data-file=-

# Store Upstash Redis URL
echo "redis://YOUR_UPSTASH_CONNECTION_STRING" | \
  gcloud secrets create redis-url-external \
    --replication-policy="automatic" \
    --data-file=-

# Store Anthropic API key
echo "YOUR_ANTHROPIC_API_KEY" | \
  gcloud secrets create anthropic-api-key \
    --replication-policy="automatic" \
    --data-file=-

# Verify
gcloud secrets list
```

### Step 4: Deploy Infrastructure with Terraform (5 minutes)

```bash
cd deploy/terraform

# Switch to minimal config
mv main.tf main-full.tf
mv main-minimal.tf main.tf

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
project_id        = "${PROJECT_ID}"
region            = "${REGION}"
environment       = "demo"
github_repository = "joshband/copy-that"

labels = {
  project     = "copy-that"
  managed_by  = "terraform"
  environment = "demo"
}
EOF

# Initialize and apply
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

**This creates:**
- Cloud Run service (with min_instances=0)
- Artifact Registry
- Service accounts
- GitHub Actions integration
- Secret Manager permissions

### Step 5: Build and Deploy (5 minutes)

```bash
# Authenticate Docker
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Get Artifact Registry URL
export ARTIFACT_REGISTRY=$(terraform output -raw artifact_registry_url)

# Build image
docker build -f Dockerfile.cloudrun -t copy-that-api:latest .

# Tag and push
docker tag copy-that-api:latest ${ARTIFACT_REGISTRY}/copy-that-api:latest
docker push ${ARTIFACT_REGISTRY}/copy-that-api:latest

# Update Cloud Run service
gcloud run services update copy-that-api-minimal \
  --image ${ARTIFACT_REGISTRY}/copy-that-api:latest \
  --region ${REGION}

# Get your public URL!
export PUBLIC_URL=$(terraform output -raw api_url)
echo "🎉 Share this URL with friends: $PUBLIC_URL"
```

### Step 6: Run Database Migrations (2 minutes)

```bash
# Option A: Run locally (connecting to Neon)
export DATABASE_URL="postgresql://YOUR_NEON_CONNECTION_STRING"
alembic upgrade head

# Option B: Run via Cloud Run job (if configured)
# Or manually via cloud shell
```

### Step 7: Test Your Deployment

```bash
# Health check
curl $PUBLIC_URL/health

# API docs (share this with family!)
open $PUBLIC_URL/docs

# Test API
curl $PUBLIC_URL/api/v1/
```

## GitHub Actions Setup

```bash
# Get values for GitHub secrets
WORKLOAD_IDENTITY=$(terraform output -raw workload_identity_provider)
SERVICE_ACCOUNT=$(terraform output -raw service_account_email)

# Add to GitHub
gh secret set GCP_PROJECT_ID -b"$PROJECT_ID"
gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER -b"$WORKLOAD_IDENTITY"
gh secret set GCP_SERVICE_ACCOUNT -b"$SERVICE_ACCOUNT"
```

## Usage & Costs

### How Billing Works

**Cloud Run (Pay-per-use):**
- First 2 million requests/month: FREE
- After that: $0.40 per million requests
- $0.00002400 per vCPU-second
- $0.00000250 per GiB-second

**Example costs for different traffic:**

| Visitors/Month | Requests | Cloud Run Cost | Total/Month |
|----------------|----------|----------------|-------------|
| Just you | 1,000 | $0.00 | $0 |
| Family (10 people) | 10,000 | $0.00 | $0 |
| Friends (100 people) | 100,000 | $0.00 | $0 |
| Popular demo (1M views) | 5,000,000 | $1.20 | $1.20 |

**Reality:** You'll likely stay at $0/month for personal use!

### Monitoring Costs

```bash
# Check current month's costs
gcloud billing accounts list
gcloud billing projects describe $PROJECT_ID

# View in Console
open "https://console.cloud.google.com/billing"
```

### Set Up Budget Alerts

```bash
# Create budget alert at $5
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="Copy That Budget Alert" \
  --budget-amount=5USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Scaling Up Later

When you're ready to move to production (paid users, compliance needs):

```bash
cd deploy/terraform

# Switch back to full config
mv main.tf main-minimal.tf
mv main-full.tf main.tf

# Update variables for production
vim terraform.tfvars

# Apply full infrastructure
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

This will add:
- Cloud SQL (private, HA database)
- Memorystore (private Redis)
- VPC networking
- Compliance features

**Cost increase:** $30-70/month → $320-890/month

## Maintenance

### Update Your App

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push

# GitHub Actions auto-deploys (if configured)
# Or manually:
docker build -f Dockerfile.cloudrun -t copy-that-api:latest .
docker push ${ARTIFACT_REGISTRY}/copy-that-api:latest
```

### Destroy Infrastructure (Stop All Costs)

```bash
# When not using for a while
cd deploy/terraform
terraform destroy -auto-approve

# Redeploy anytime with
terraform apply
```

## Troubleshooting

### Cloud Run service returns 503

**Check deployment:**
```bash
gcloud run services describe copy-that-api-minimal --region us-central1

# View logs
gcloud run services logs read copy-that-api-minimal --region us-central1 --limit 50
```

### Database connection fails

**Test Neon connection:**
```bash
psql "postgresql://YOUR_NEON_CONNECTION_STRING"
```

**Check secret:**
```bash
gcloud secrets versions access latest --secret=database-url-external
```

### Out of free tier limits

**Neon (100 compute hours):**
- Enable auto-pause (enabled by default)
- Upgrade to Pro ($19/month for 750 hours)

**Upstash (10K requests/day):**
- Monitor usage in dashboard
- Upgrade to $10/month for 100K requests/day

## Security Notes

### What's Secure
- ✅ HTTPS everywhere (automatic)
- ✅ Secrets in Secret Manager (encrypted)
- ✅ TLS for database connections
- ✅ Authentication for admin endpoints
- ✅ CORS protection

### What's Not Enterprise-Grade
- ⚠️ Database on public internet (not private VPC)
- ⚠️ No HIPAA/PCI DSS compliance
- ⚠️ Shared infrastructure (free tiers)
- ⚠️ No SLA guarantees

**Verdict:** Fine for personal/demo, upgrade for production

## FAQs

**Q: Can I use this for a real business?**
A: For MVP/beta testing, yes. For production with paid users, upgrade to full GCP.

**Q: What if I exceed free tier limits?**
A: Neon/Upstash will either throttle or upgrade you. Set billing alerts!

**Q: Can I use a custom domain?**
A: Yes! Cloud Run supports custom domains (verify in Search Console).

**Q: Is my data safe?**
A: Yes for personal use. Neon/Upstash use encryption and are SOC 2 certified.

**Q: Can family/friends upload images?**
A: Yes, Cloud Run handles uploads. Consider Cloud Storage for large files.

**Q: How do I back up my database?**
A: Neon has automatic backups. Export manually: `pg_dump > backup.sql`

## Comparison: When to Use Which Setup

| Feature | Minimal (External) | Full (GCP) |
|---------|-------------------|------------|
| **Cost/month** | $0-5 | $30-70 (staging) / $320-890 (prod) |
| **Setup time** | 30 minutes | 60 minutes |
| **Ideal for** | Personal, demos | Production, compliance |
| **Database** | Neon.tech (free) | Cloud SQL (private) |
| **Redis** | Upstash (free) | Memorystore (private) |
| **Networking** | Public internet | Private VPC |
| **Compliance** | Basic | SOC 2, HIPAA, PCI DSS |
| **SLA** | None | 99.95% |
| **Auto-scale** | 0-5 instances | 0-100 instances |
| **Backups** | Automatic (Neon) | Point-in-time recovery |

## Conclusion

**For your use case (personal project + shareable demo):**

✅ **Use Minimal Setup**
- Free/cheap ($0-5/month)
- Fast to set up (30 min)
- Perfect for demos
- Secure enough

**Upgrade to Full when:**
- You have paying customers
- Need compliance (SOC 2, HIPAA)
- Want enterprise SLA
- Need high traffic (>10K req/day)

---

**Ready to share with family and friends!** 🎉

Your URL: `https://copy-that-api-minimal-xxxxx-uc.a.run.app`

**Last Updated**: 2025-11-19
