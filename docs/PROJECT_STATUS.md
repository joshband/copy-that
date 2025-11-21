# Copy That: Project Status & Deployment Guide

**Last Updated**: 2025-11-21 | **Version**: v0.4.0 | **Status**: Color Token MVP Complete

---

## Current State Summary

The color token extraction pipeline is **production-ready**. Core functionality is complete with session-based batch extraction, Delta-E deduplication, and multi-format export (W3C/CSS/React/HTML).

---

## 1. Roadmap Phases

### Now (v0.4.x) - In Progress
- [ ] Stabilize session/library/export flows
- [ ] Frontend polish: educational components, inspector/playground
- [x] API refactoring into modular routers
- [x] Frontend type parity with backend
- [ ] Ops: finalize runbook, troubleshooting, Terraform/Alembic docs

### Next (Phase 5) - Pending
- [ ] Spacing tokens with SAM-assisted detection
- [ ] Typography tokens (schema, extractor, export)
- [ ] API examples & quickstart scripts for new token types

### Later (Phase 6+) - Pending
- [ ] Component tokens (button/input/card detection)
- [ ] Multi-modal inputs (video/audio/text)
- [ ] Plugins (Figma/Sketch)
- [ ] CI-based export validation

---

## 2. Color Token Completeness

### Backend Status
| Component | Status | Notes |
|-----------|--------|-------|
| Extraction | ✅ Complete | AI + local algorithms working |
| Aggregation | ✅ Complete | Delta-E deduplication (threshold 2.0) |
| Export | ✅ Complete | W3C/CSS/React/HTML formats |
| Curation UI | 🔄 Partial | Role assignment backend exists, UI needs polish |
| Educational | 🔄 Partial | HarmonyVisualizer, AccessibilityVisualizer need wiring |

### Frontend-Backend Parity
**Status**: ✅ Fixed (2025-11-21)

The `ColorToken` interface now includes all 38 fields from the backend model:

**Core**: id, project_id, extraction_job_id, hex, rgb, hsl, hsv, name

**Design**: design_intent, semantic_names, category

**Analysis**: confidence, harmony, temperature, extraction_metadata, saturation_level, lightness_level, usage

**Metrics**: count, prominence_percentage

**Accessibility**: wcag_contrast_on_white, wcag_contrast_on_black, wcag_aa_compliant_text, wcag_aaa_compliant_text, wcag_aa_compliant_normal, wcag_aaa_compliant_normal, colorblind_safe

**Variants**: tint_color, shade_color, tone_color

**Advanced**: closest_web_safe, closest_css_named, delta_e_to_dominant, is_neutral

**ML**: kmeans_cluster_id, sam_segmentation_mask, clip_embeddings, histogram_significance

**Curation**: library_id, role, provenance

---

## 3. Infrastructure Recommendations

### High Priority
1. **API Authentication** - Cloud Run is currently public (`allUsers` IAM binding)
2. **Celery Workers for Production** - No Cloud Run Jobs configured yet
3. **Rate Limiting** - Add Cloud Armor rules

### Medium Priority
4. **Cloud Monitoring Alerts** - Prometheus in docker-compose but not in GCP
5. **Domain/SSL Setup** - Variable exists but no certificate resources
6. **Database Tier** - Upgrade from `db-f1-micro` to `db-custom-2-7680` for production

---

## 4. GCP Production Deployment

### Prerequisites
- GCP Project with billing enabled
- `gcloud` CLI authenticated
- Terraform installed

### Existing Infrastructure (in `deploy/terraform/`)
- ✅ Cloud SQL PostgreSQL 16
- ✅ Memorystore Redis 7.0
- ✅ Cloud Run service + migrations job
- ✅ VPC networking
- ✅ Service accounts + IAM
- ✅ Artifact Registry for Docker images

### Deployment Steps

```bash
# 1. Set GCP project
gcloud config set project YOUR_PROJECT_ID

# 2. Create secrets in Secret Manager
gcloud secrets create anthropic-api-key --replication-policy="automatic"
echo -n "your-anthropic-key" | gcloud secrets versions add anthropic-api-key --data-file=-

gcloud secrets create secret-key --replication-policy="automatic"
openssl rand -hex 32 | gcloud secrets versions add secret-key --data-file=-

# 3. Initialize Terraform
cd deploy/terraform
terraform init

# 4. Create terraform.tfvars
cat > terraform.tfvars <<EOF
project_id = "your-project-id"
region = "us-central1"
environment = "staging"  # or "production"
domain_name = "copythat.yourdomain.com"
EOF

# 5. Plan and apply
terraform plan
terraform apply

# 6. Build and push Docker image
cd ../..
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/copy-that:latest

# 7. Deploy updates (Terraform handles Cloud Run)
cd deploy/terraform
terraform apply
```

### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection (auto from Cloud SQL) | Yes |
| `REDIS_URL` | Redis connection (auto from Memorystore) | Yes |
| `ANTHROPIC_API_KEY` | Claude API key for color extraction | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `CORS_ORIGINS` | Allowed frontend origins | Yes |
| `ENVIRONMENT` | local/staging/production | Yes |
| `GCS_BUCKET` | Image storage bucket | Optional |
| `SENTRY_DSN` | Error tracking | Optional |

### Production Checklist

#### Security
- [ ] Create GCP Secret Manager secrets for API keys
- [ ] Configure Cloud Run authentication (remove `allUsers` IAM binding)
- [ ] Set up Cloud Armor for DDoS protection
- [ ] Enable VPC Service Controls

#### Infrastructure
- [ ] Set up custom domain with SSL certificate
- [ ] Configure production database tier (`db-custom-2-7680`)
- [ ] Enable Redis STANDARD_HA for high availability
- [ ] Add Celery workers as Cloud Run Jobs

#### Monitoring
- [ ] Set up Cloud Monitoring alerting policies
- [ ] Configure log-based metrics
- [ ] Enable Cloud Trace for performance monitoring

#### Backup & DR
- [ ] Test database backup restoration
- [ ] Document disaster recovery procedures
- [ ] Set up cross-region replication (optional)

---

## 5. Local Development

### Quick Start
```bash
# Backend
cd /home/user/copy-that
cp .env.example .env  # Configure your API keys
docker-compose up -d postgres redis
uvicorn src.copy_that.interfaces.api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Frontend tests by area (avoids timeout issues)
npm run test:fast      # Store + config only
npm run test:store     # Token store tests
npm run test:config    # Config tests
npm run test:components # Component tests

# Backend tests
pytest src/copy_that/tests/
```

---

## 6. Known Issues & Workarounds

### Test Timeout on Global Run
**Issue**: Running all frontend tests together causes timeout
**Workaround**: Use `npm run test:fast` or run by area

### Celery Workers in Production
**Issue**: No Cloud Run Jobs configured for async tasks
**Workaround**: Use Cloud Tasks or deploy Celery as separate Cloud Run service

---

## 7. Next Session Priorities

### Option A: Deploy to GCP Staging
- Run Terraform to create infrastructure
- Deploy application to Cloud Run
- Verify end-to-end flow
- **Time estimate**: 2-3 hours

### Option B: Wire Educational Components
- Connect HarmonyVisualizer to harmony field
- Connect AccessibilityVisualizer to WCAG fields
- Display tint/shade/tone variants
- **Time estimate**: 1-2 hours

### Option C: Curation UI Polish
- Build role assignment UI
- Connect to curate_library endpoint
- Add token renaming/notes
- **Time estimate**: 2-3 hours

---

## Related Documentation

- [Architecture Overview](architecture/architecture_overview.md) - System design and patterns
- [ROADMAP.md](../ROADMAP.md) - Phases 5-10 planning
- [Phase 4 Workflow](workflows/phase_4_color_vertical_slice.md) - Current implementation details
- [.env.example](../.env.example) - All environment variables

---

**Questions?** Check the architecture overview or ROADMAP for additional context.
