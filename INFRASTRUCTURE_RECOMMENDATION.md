# Infrastructure Recommendation: Affordable & Best Practice

**Date:** 2025-12-12
**Goal:** Local Dev, GCP Dev, Production GCP - Free/Affordable + Best Practice

---

## Recommended 3-Environment Setup

### Environment Breakdown

| Environment | Purpose | Cost | Infrastructure |
|-------------|---------|------|----------------|
| **Local Dev** | Development on your machine | $0 | Docker Compose + Neon Local |
| **GCP Dev** | CI/CD + Integration Testing | ~$0-5/month | Cloud Run (min=0) + Neon Free Tier |
| **GCP Production** | Live application | ~$10-30/month | Cloud Run + Neon Pro ($19) |

---

## Environment Details

### 1. Local Development (FREE)

**Stack:**
```
Docker Compose:
  - Frontend (Vite dev server)
  - Backend (FastAPI with hot reload)
  - Neon Local (PostgreSQL 17)
  - Redis (optional - for caching)
```

**Connection:**
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/main
REDIS_URL=redis://localhost:6379/0
```

**Benefits:**
- ✅ $0 cost
- ✅ Fast iteration
- ✅ Offline development
- ✅ No cloud dependencies

**Setup:**
```bash
# Install Neon CLI
brew install neonctl  # or: npm install -g neonctl

# Start services
docker-compose up -d
neonctl local start

# Develop
pnpm dev        # Frontend on :5173
pnpm dev:backend # Backend on :8000
```

---

### 2. GCP Dev (FREE - $5/month)

**Purpose:**
- CI/CD testing (GitHub Actions)
- Integration testing
- Preview deployments
- Staging environment

**Stack:**
```
Cloud Run (us-central1):
  - Min instances: 0 (scale to zero = FREE when idle)
  - Max instances: 3
  - CPU: 1
  - Memory: 512Mi
  - Estimated: $0-2/month (only pay when running)

Neon Database (Free Tier):
  - Branch: dev or staging
  - Storage: 3GB (free)
  - Compute: Shared (free)
  - Auto-suspend: 5 minutes
  - Estimated: $0/month

Artifact Registry:
  - Docker images: <1GB
  - Estimated: $0.10/month

GitHub Actions:
  - 2,000 minutes/month free (public repos)
  - Estimated: $0/month

TOTAL: ~$0-3/month
```

**Infrastructure:**
- Cloud Run (serverless, pay-per-use)
- Neon Free Tier (3GB database)
- Artifact Registry (store Docker images)
- No VPC, no NAT, no Cloud SQL (expensive!)

**Best for:**
- Running tests in CI
- Deploying PR previews
- Testing before production

---

### 3. GCP Production ($10-30/month)

**Stack:**
```
Cloud Run (us-central1):
  - Min instances: 1 (always-on for fast response)
  - Max instances: 10
  - CPU: 2
  - Memory: 1Gi
  - Estimated: $15-25/month

Neon Database (Pro Tier):
  - Branch: main
  - Storage: 10GB
  - Dedicated compute
  - Daily backups
  - Cost: $19/month (Pro plan)

Artifact Registry:
  - Same as dev
  - Estimated: $0.10/month

Cloud Monitoring (optional):
  - Uptime checks
  - Alerts
  - Estimated: $0-5/month

TOTAL: ~$35-50/month
```

**Best for:**
- Production traffic
- Real users
- SLA requirements
- Performance guarantees

---

## Terraform Consolidation Recommendation

Based on GCP interrogation and your needs:

### RECOMMENDATION: Archive root `terraform/`, Use `deploy/terraform/`

**Why:**
1. **Modular Structure** - `deploy/terraform/` is better organized
2. **Neon Integration** - Already has neon.tf (I just fixed it)
3. **Future-Ready** - Designed for multi-environment
4. **Better Docs** - Comprehensive README with cost estimates
5. **Industry Standard** - Separate deploy configs from app code

**Current GCP Resources (from interrogation):**
```
Cloud Run Services (3):
  - copy-that (managed by root terraform/)
  - copy-that-api (managed by root terraform/)
  - copy-that-api-production (???)

Artifact Registries (3):
  - cloud-run-repo
  - cloud-run-source-deploy
  - copy-that

Service Accounts (3):
  - copy-that-api-sa
  - github-actions
  - (compute default)

Workload Identity: EXISTS ✅
```

**Problem:** Root `terraform/` is actively managing resources!

---

## Safe Migration Plan

### Step 1: Identify What's Managed Where

```bash
# Root terraform (currently managing production resources)
cd /Users/noisebox/Documents/3_Development/Repos/copy-that/terraform
terraform state list
terraform show > ~/current-terraform-state.txt

# Deploy terraform (not initialized yet)
cd /Users/noisebox/Documents/3_Development/Repos/copy-that/deploy/terraform
# Not managing anything yet
```

### Step 2: Import to deploy/terraform

```bash
cd /Users/noisebox/Documents/3_Development/Repos/copy-that/deploy/terraform

# Initialize with Neon provider
terraform init

# Import existing Cloud Run service
terraform import google_cloud_run_service.api copy-that-api

# Import service account
terraform import google_service_account.cloudrun_sa copy-that-api-sa

# Import other resources...
```

### Step 3: Verify and Switch

```bash
# Plan (should show no changes if import worked)
terraform plan

# If clean, archive root terraform/
mv terraform/ ~/Documents/copy-that-archive/terraform-root-archived/

# Update README to point to deploy/terraform
```

---

## Affordable FREE/CHEAP Infrastructure Recommendations

### 1. Use Neon Instead of Cloud SQL

**Cloud SQL (Expensive):**
- Minimum: ~$15/month (db-f1-micro)
- HA setup: ~$120/month
- Always running, even when idle

**Neon (Affordable):**
- Free tier: $0/month (3GB, shared compute)
- Pro tier: $19/month (10GB, dedicated compute, backups)
- Auto-suspend when idle (saves money!)
- Branch-based workflows (dev/staging/prod branches)

**Winner:** Neon saves $96-100/month minimum! ✅

### 2. Cloud Run with Scale-to-Zero

**Instead of:**
- Google Kubernetes Engine (GKE): ~$75/month minimum
- Compute Engine VMs: ~$25/month always-on

**Use:**
- Cloud Run with `min_instances = 0` for dev
- Cloud Run with `min_instances = 1` for production (~$15/month)
- Only pay when traffic comes in

**Winner:** Cloud Run saves ~$60/month on dev! ✅

### 3. Skip VPC/NAT for Dev

**VPC + Cloud NAT (Expensive):**
- Cloud NAT: ~$45/month
- VPC connector: ~$10/month
- Total: ~$55/month just for networking!

**Instead:**
- Public Cloud Run (free networking)
- Use authentication/API keys for security
- Neon has built-in SSL

**Winner:** Skip VPC saves ~$55/month! ✅

### 4. Use GitHub Actions (Free)

**Instead of:**
- Cloud Build: ~$0.003/build-minute
- 1000 builds/month = ~$15-30/month

**Use:**
- GitHub Actions: 2,000 minutes/month FREE for public repos
- Unlimited for private repos with GitHub Pro ($4/month)

**Winner:** GitHub Actions saves ~$15-30/month! ✅

---

## Final Recommended Stack

### Local Development ($0/month)
```
✅ Docker Compose
✅ Neon Local (or Docker PostgreSQL)
✅ Redis (Docker)
✅ Vite dev server
✅ FastAPI with uvicorn --reload
```

### GCP Dev/Staging ($0-5/month)
```
✅ Cloud Run (min_instances=0, scale-to-zero)
✅ Neon Free Tier (3GB database)
✅ Artifact Registry ($0.10/month)
✅ GitHub Actions CI/CD (free)
✅ No VPC, no NAT, no Cloud SQL
```

### GCP Production ($35-50/month)
```
✅ Cloud Run (min_instances=1, always-on)
✅ Neon Pro ($19/month, 10GB, backups)
✅ Artifact Registry ($0.10/month)
✅ Cloud Monitoring/Logging ($5/month)
✅ Custom domain + SSL (free with Cloud Run)
```

**Total Cost:**
- Local: $0
- Dev: ~$1/month
- Production: ~$40/month
- **GRAND TOTAL: ~$40/month** (vs $200+/month with Cloud SQL + VPC!)

---

## Infrastructure as Code Strategy

### Recommended Terraform Structure

```
deploy/terraform/
├── main.tf             # Providers (Google + Neon)
├── variables.tf        # All variables
├── outputs.tf          # Connection strings, URLs
├── neon.tf             # Neon database (all environments)
├── artifact_registry.tf # Docker images
├── cloudrun.tf         # Cloud Run services
├── iam.tf              # Service accounts, Workload Identity
├── secrets.tf          # Secret Manager (API keys)
└── terraform.tfvars    # Your values (gitignored)
```

**Use Terraform Workspaces for environments:**
```bash
terraform workspace new dev
terraform workspace new production

# Deploy to dev
terraform workspace select dev
terraform apply -var="environment=dev"

# Deploy to production
terraform workspace select production
terraform apply -var="environment=production"
```

---

## Best Practices

### 1. Use Neon Branches for Environments

```
Neon Project: copy-that
├── main branch (production)
├── dev branch (development)
└── ci-test branch (GitHub Actions)
```

**Benefits:**
- FREE branches (unlimited on free tier!)
- Instant database replication
- Test migrations on dev before production
- No Cloud SQL needed

### 2. Cloud Run Auto-Scaling

**Dev/Staging:**
```hcl
min_instances = 0  # FREE when idle!
max_instances = 3
cpu = 1
memory = 512Mi
```

**Production:**
```hcl
min_instances = 1  # Always-on for speed
max_instances = 10
cpu = 2
memory = 1Gi
```

### 3. Use Secret Manager (Not Environment Variables)

```hcl
# Store secrets in Secret Manager
resource "google_secret_manager_secret" "anthropic_key" {
  secret_id = "anthropic-api-key"
}

# Cloud Run accesses via IAM (secure!)
```

### 4. Leverage GitHub Actions FREE Tier

**Instead of Cloud Build:**
```yaml
# .github/workflows/deploy.yml
# Uses GitHub Actions runners (FREE)
# Deploys to Cloud Run
# Runs migrations
# Smoke tests
```

---

## Terraform Directory Decision

### KEEP: `deploy/terraform/` ✅

**Reasons:**
1. ✅ Modular structure (7 files vs 1 monolith)
2. ✅ Better documentation (README with costs)
3. ✅ Includes Neon integration (neon.tf)
4. ✅ Workspace-ready (dev/prod separation)
5. ✅ Matches industry standards

### ARCHIVE: `terraform/` (root)

**Reasons:**
1. ⚠️ Currently managing production resources
2. ⚠️ Monolithic (all in main.tf)
3. ⚠️ Less documentation
4. ⚠️ Harder to maintain
5. ⚠️ Duplicate of deploy/terraform

**Migration Strategy:**
```bash
# 1. Export current state
cd deploy/terraform/
terraform state pull > ~/terraform-root-backup.tfstate

# 2. List managed resources
terraform state list > ~/resources-to-migrate.txt

# 3. Import into deploy/terraform
cd ../deploy/terraform/
terraform init

# 4. Import each resource (from list)
while read resource; do
  terraform import "$resource" "$(get_resource_id)"
done < ~/resources-to-migrate.txt

# 5. Verify
terraform plan  # Should show "No changes"

# 6. Archive old terraform/
mv /Users/noisebox/Documents/3_Development/Repos/copy-that/terraform \
   ~/Documents/copy-that-archive/terraform-root-legacy/
```

---

## Cost Breakdown Comparison

### Option A: Your Current Setup (Unclear)
```
Cloud Run: 3 services (unknown cost)
Neon: Manual (no Terraform)
Total: Unknown
```

### Option B: Recommended (Affordable)
```
Local Dev: $0
GCP Dev: ~$1/month (scale-to-zero Cloud Run + Neon free tier)
Production: ~$40/month (always-on Cloud Run + Neon Pro)
TOTAL: ~$40/month
```

### Option C: "Enterprise" (Expensive)
```
Cloud SQL HA: ~$120/month
Cloud NAT: ~$45/month
Redis HA: ~$50/month
VPC: ~$10/month
Cloud Run (prod): ~$30/month
TOTAL: ~$255/month
```

**Recommendation:** Option B saves $215/month! ✅

---

## Immediate Action Plan

### Step 1: Fix Duplicate Terraform Issue

**Problem:**
- Root `terraform/` is managing current production resources
- `deploy/terraform/` is newer but not applied
- Both exist = confusion

**Solution:**
- Keep `deploy/terraform/` (better structure + Neon)
- Migrate resources from root → deploy
- Archive root `terraform/`

### Step 2: Use deploy/terraform Going Forward

```bash
cd deploy/terraform/

# Initialize
terraform init

# Plan (check what would be created)
export TF_VAR_neon_api_key="your-neon-api-key"
terraform plan

# Apply when ready
terraform apply
```

### Step 3: Update Documentation

- Point all docs to `deploy/terraform/`
- Archive references to root `terraform/`
- Update README with new structure

---

## Neon Branch Strategy (Best Practice + Affordable)

### Recommended Neon Setup

```
Neon Project: copy-that-platform (ONE project for all environments)

Branches:
├── main (production data)
│   ├── Compute: 0.25-1.0 CU
│   └── Cost: $19/month (Pro plan for backups)
│
├── dev (development data - FREE)
│   ├── Parent: main
│   ├── Compute: Shared (auto-suspend)
│   └── Cost: $0/month (free tier)
│
└── ci-test (GitHub Actions - FREE)
    ├── Parent: main
    ├── Reset daily (fresh data)
    ├── Compute: Shared (auto-suspend)
    └── Cost: $0/month (free tier)
```

**Benefits:**
- ✅ ONE project (simpler management)
- ✅ Branches are FREE
- ✅ Instant duplication of prod data to dev/test
- ✅ Test migrations safely on dev branch
- ✅ Total cost: $19/month for Pro (vs $120/month for Cloud SQL!)

---

## Environment Variable Strategy

### Local Development (.env.local)
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/main
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### GCP Dev (Secret Manager)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@neon-host/neondb  # Dev branch
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ALLOWED_ORIGINS=https://dev.copy-that.com
```

### GCP Production (Secret Manager)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@neon-host/neondb  # Main branch
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://copy-that.com
```

---

## What to Remove (Cost Savings)

### Remove from deploy/terraform/ (If Exists):

❌ **cloudsql.tf** - Use Neon instead ($100/month savings)
❌ **redis.tf** - Use Neon for simple caching or Upstash ($40/month savings)
❌ **networking.tf** - No VPC needed for dev ($55/month savings)

Keep only:
✅ **main.tf** - Providers, service accounts
✅ **neon.tf** - Database (I just created this!)
✅ **cloudrun.tf** - Application hosting
✅ **artifact_registry.tf** - Docker images
✅ **iam.tf** - Security (Workload Identity)
✅ **secrets.tf** - API keys

**Total savings: ~$195/month by using Neon + simpler infrastructure!**

---

## Migration Checklist

### Phase 1: Consolidate Terraform (Today)

- [ ] Back up root `terraform/` state
- [ ] List resources managed by root terraform
- [ ] Import resources into `deploy/terraform/`
- [ ] Verify `terraform plan` shows no changes
- [ ] Archive root `terraform/` directory
- [ ] Update all documentation references

### Phase 2: Optimize for Cost (Next Session)

- [ ] Remove Cloud SQL config (if exists)
- [ ] Remove VPC/NAT config (if not needed)
- [ ] Remove Redis config (use Neon or Upstash)
- [ ] Set Cloud Run `min_instances=0` for dev
- [ ] Test scale-to-zero functionality

### Phase 3: Apply Neon Terraform (Next Session)

- [ ] Run `terraform init` in deploy/terraform
- [ ] Run `terraform plan` to review Neon resources
- [ ] Run `terraform apply` to create Neon infrastructure
- [ ] Get connection strings from `terraform output`
- [ ] Update GitHub Secrets with Terraform-managed values

---

## Quick Win: Just Get CI Green (For Now)

**If you want badges green TODAY without Terraform migration:**

1. ✅ Keep using manual Neon setup (works fine!)
2. ✅ Wait for CI to complete (~10 more minutes)
3. ✅ CI badge should turn green
4. ✅ Codecov badge should show coverage
5. 📋 Migrate to `deploy/terraform/` next session

**This is perfectly fine!** Terraform migration can wait. Focus on green badges first.

---

## Cost Summary: Recommended vs Current

### Recommended Setup (Affordable)

| Item | Cost/Month |
|------|------------|
| Local Dev | $0 |
| GCP Dev (Cloud Run + Neon Free) | ~$1 |
| Production (Cloud Run + Neon Pro) | ~$40 |
| **TOTAL** | **~$40/month** |

### Alternative "Enterprise" Setup (Expensive)

| Item | Cost/Month |
|------|------------|
| Local Dev | $0 |
| Cloud SQL + HA | ~$120 |
| VPC + NAT | ~$55 |
| Redis HA | ~$50 |
| Cloud Run | ~$30 |
| **TOTAL** | **~$255/month** |

**Savings with Neon + Simplified Infrastructure: ~$215/month (84% reduction!)**

---

## Final Recommendation

**For CI Badges (Immediate):**
- ✅ Use current manual Neon setup
- ✅ Wait for CI to complete
- ✅ Get green badges TODAY

**For Infrastructure (Next Session):**
- ✅ Migrate to `deploy/terraform/`
- ✅ Apply Neon Terraform config
- ✅ Remove expensive components (Cloud SQL, VPC, Redis)
- ✅ Use 3 environments: Local, GCP Dev, GCP Prod
- ✅ Target cost: ~$40/month total

**Best of both worlds:** Green badges today, clean infrastructure tomorrow! 🎉

---

**Last Updated:** 2025-12-12
**Status:** Ready for execution
