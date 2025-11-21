# Deployment Options

Choose the right infrastructure setup for your needs.

## Quick Comparison

| | **Local** | **Minimal Cloud** | **Full Cloud** |
|---|-----------|------------------|----------------|
| **Cost** | FREE | $0-5/month | $30-70/month |
| **Setup Time** | 5 min | 30 min | 60 min |
| **Best For** | Development | Personal/Demo | Production |
| **Public URL** | ❌ No | ✅ Yes | ✅ Yes |
| **Database** | Local Postgres | Neon.tech (free) | Cloud SQL (private) |
| **Redis** | Local Redis | Upstash (free) | Memorystore (private) |
| **Networking** | localhost | Public internet | Private VPC |
| **Compliance** | N/A | Basic | Enterprise |
| **Scalability** | Single machine | 0-5 instances | 0-100 instances |
| **Teardown** | Stop containers | `terraform destroy` | `terraform destroy` |

---

## Option 1: Local Development (FREE)

**Perfect for:**
- Daily development
- Testing features
- Learning the codebase
- No internet needed

### Setup

```bash
# Start everything
docker-compose up

# Access
http://localhost:8000
http://localhost:8000/docs
```

### Pros
- ✅ Completely free
- ✅ Fast iteration
- ✅ Full control
- ✅ Works offline
- ✅ No cloud costs

### Cons
- ❌ No public URL
- ❌ Can't share with others
- ❌ Requires local machine running
- ❌ Limited by laptop resources

### When to Use
- Writing code daily
- Running tests
- Debugging issues
- Prototyping features

---

## Option 2: Minimal Cloud (Recommended for You!)

**Perfect for:**
- Personal projects
- Sharing with family/friends
- Portfolio demos
- MVP testing
- Budget-conscious deployment

### Architecture

```
Internet
   ↓
Cloud Run (pay-per-use)
   ↓
Neon.tech (free Postgres) + Upstash (free Redis)
```

### Setup

Follow: [setup/setup_minimal.md](setup/setup_minimal.md)

**Quick version:**
```bash
# 1. Create free accounts
https://neon.tech
https://upstash.com

# 2. Deploy with Terraform
cd deploy/terraform
mv main.tf main-full.tf
mv main-minimal.tf main.tf
terraform init && terraform apply

# 3. Get public URL
terraform output api_url
```

### Costs Breakdown

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 0-1K requests/day | $0.00 |
| Artifact Registry | <1GB images | $0.10/mo |
| Neon.tech | 3GB storage | FREE |
| Upstash | 10K req/day | FREE |
| **Total** | | **$0-5/month** |

### Pros
- ✅ Public URL to share
- ✅ Near-zero cost
- ✅ Auto-scaling (0-5 instances)
- ✅ Automatic HTTPS
- ✅ Quick setup (30 min)
- ✅ Easy teardown
- ✅ Secure for personal use

### Cons
- ⚠️ Not enterprise-grade
- ⚠️ No compliance certifications
- ⚠️ Free tier limits (3GB, 10K req/day)
- ⚠️ Shared infrastructure
- ⚠️ No SLA guarantees

### When to Use
- **NOW**: Personal project phase ← YOU ARE HERE
- Sharing with friends/family
- Job interviews (show your work)
- Beta testing (small audience)
- MVP validation

### When to Upgrade
- Paying customers
- Need compliance (SOC 2, HIPAA)
- >10K requests/day
- Enterprise clients

---

## Option 3: Full Cloud Infrastructure

**Perfect for:**
- Production applications
- Compliance requirements
- Enterprise customers
- High traffic (>100K req/day)
- Mission-critical services

### Architecture

```
Internet
   ↓
Cloud Run (multi-region)
   ↓
Private VPC
   ├─→ Cloud SQL (HA, backups)
   ├─→ Memorystore (HA)
   └─→ Cloud NAT (outbound)
```

### Setup

Follow: [setup/infrastructure_setup.md](setup/infrastructure_setup.md)

**Quick version:**
```bash
cd deploy/terraform
terraform init
terraform apply
```

### Costs Breakdown

**Staging:**
| Service | Configuration | Cost |
|---------|--------------|------|
| Cloud Run | 1 CPU, 512Mi, 0-10 instances | $10-30 |
| Cloud SQL | db-f1-micro | $7-15 |
| Memorystore | BASIC, 1GB | $5-10 |
| VPC/NAT | Standard | $5-10 |
| **Total** | | **$30-70/month** |

**Production:**
| Service | Configuration | Cost |
|---------|--------------|------|
| Cloud Run | 2 CPU, 1Gi, 1-100 instances | $100-500 |
| Cloud SQL | db-custom-2-7680 HA | $150-250 |
| Memorystore | STANDARD_HA, 5GB | $50-100 |
| VPC/NAT | Standard | $20-40 |
| **Total** | | **$320-890/month** |

### Pros
- ✅ Enterprise-grade security
- ✅ SOC 2, HIPAA, PCI DSS compliant
- ✅ 99.95% uptime SLA
- ✅ Private VPC networking
- ✅ Point-in-time recovery
- ✅ High availability (multi-zone)
- ✅ Professional support
- ✅ Unlimited scaling

### Cons
- ❌ Higher costs ($30-890/month)
- ❌ More complex setup
- ❌ Overkill for personal projects
- ❌ Always-on costs (even when idle)

### When to Use
- Paying customers
- Enterprise clients
- Compliance requirements
- High traffic (>100K req/day)
- Mission-critical services
- When budget allows

---

## Migration Path

### Phase 1: Development (Now)
```
Local docker-compose
Cost: $0
```

### Phase 2: Personal Demo (Now → 3 months)
```
Minimal Cloud (Neon + Upstash)
Cost: $0-5/month
```
📍 **YOU ARE HERE** (Best choice for your use case!)

### Phase 3: Beta Testing (3-6 months)
```
Full Cloud Staging
Cost: $30-70/month
```

### Phase 4: Production (6+ months)
```
Full Cloud Production
Cost: $320-890/month
```

---

## Decision Matrix

### Use Local If:
- [ ] Just coding/testing
- [ ] No need to share URL
- [ ] Want zero cloud costs
- [ ] Learning/experimenting

### Use Minimal Cloud If: ← **RECOMMENDED FOR YOU**
- [x] Personal project
- [x] Want to share with friends/family
- [x] Budget-conscious (<$5/month)
- [x] No sensitive data yet
- [x] No compliance needs
- [x] Quick demos/portfolio

### Use Full Cloud If:
- [ ] Production application
- [ ] Paying customers
- [ ] Need compliance (SOC 2, HIPAA)
- [ ] Enterprise clients
- [ ] High traffic (>100K req/day)
- [ ] Budget allows ($30-890/month)

---

## Your Recommended Path

Based on **"personal project + shareable URL for family/friends"**:

### Step 1: Develop Locally (Today)
```bash
docker-compose up
# Build features, test, iterate
```

### Step 2: Deploy Minimal Cloud (When ready to share)
```bash
# Follow setup/setup_minimal.md
# Get public URL
# Share with friends: https://your-app.run.app
```

### Step 3: Keep Costs Low
```bash
# Only runs when URL is accessed
# Auto-scales to zero when idle
# Budget: ~$0-5/month
```

### Step 4: Upgrade When Needed (Future)
```bash
# If project takes off:
# - Switch to full Terraform config
# - Upgrade Neon → Cloud SQL
# - Upgrade Upstash → Memorystore
# - Budget: ~$320-890/month
```

---

## Quick Start Commands

### Local Development
```bash
docker-compose up
open http://localhost:8000/docs
```

### Minimal Cloud Deployment
```bash
cd deploy/terraform
mv main.tf main-full.tf
mv main-minimal.tf main.tf
terraform init
terraform apply
# Share: $(terraform output -raw api_url)
```

### Full Cloud Deployment
```bash
cd deploy/terraform
terraform init
terraform apply
# Production URL: $(terraform output -raw api_url)
```

---

## Cost Monitoring

### Set Up Budget Alerts (All Options)

```bash
gcloud billing budgets create \
  --billing-account=YOUR_ACCOUNT \
  --display-name="Copy That Alert" \
  --budget-amount=10USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90
```

### Check Current Costs

```bash
# View in Console
open "https://console.cloud.google.com/billing"

# Or via CLI
gcloud billing accounts list
```

---

## Support

- **Local Issues**: Check docker-compose logs
- **Minimal Cloud**: See [setup/setup_minimal.md](setup/setup_minimal.md)
- **Full Cloud**: See [setup/infrastructure_setup.md](setup/infrastructure_setup.md)
- **Questions**: Open GitHub issue

---

## TL;DR - What Should I Use?

**Right now?** → **Minimal Cloud Setup**

- Public URL for demos: ✅
- Share with friends/family: ✅
- Cost: ~$0-5/month: ✅
- Easy setup: ✅
- Secure enough: ✅

Follow: [setup/setup_minimal.md](setup/setup_minimal.md)

**Later (if it takes off)?** → **Full Cloud Setup**

Follow: [setup/infrastructure_setup.md](setup/infrastructure_setup.md)

---

**Last Updated**: 2025-11-19
