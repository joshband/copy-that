# CI Badge Green Plan

**Goal:** Get all repository badges showing green status
**Created:** 2025-12-12
**Status:** Ready for execution

---

## Current Badge Status

Based on README.md line 5-11, we have 7 badges:

| Badge | URL | Status | Notes |
|-------|-----|--------|-------|
| CI | `ci.yml` workflow | 🔴 Unknown | Comprehensive workflow with security, lint, test, docker |
| Build | `build.yml` workflow | 🔴 Unknown | Docker image build + push to GCP Artifact Registry |
| Deploy | `deploy.yml` workflow | 🔴 Unknown | Cloud Run deployment (staging + production) |
| codecov | codecov.io | 🔴 Unknown | Code coverage reporting |
| Python 3.12+ | Static badge | 🟢 Green | Already correct |
| Code style: Ruff | Static badge | 🟢 Green | Already correct |
| License: MIT | Static badge | 🟢 Green | Already correct |

---

## Analysis of CI Workflow

### Workflow: `.github/workflows/ci.yml`

**Jobs:**
1. **Security** (Lines 13-53)
   - pip-audit (dependency vulnerabilities) - `continue-on-error: true`
   - Bandit (Python security linter)
   - Gitleaks (secret detection)
   - ✅ **Should pass** - Security scans are informational

2. **Lint** (Lines 55-84)
   - Ruff linter check
   - Ruff formatter check
   - mypy type checker
   - ✅ **Should pass** - mypy overrides are in pyproject.toml

3. **Test** (Lines 86-184)
   - Requires PostgreSQL + Redis services
   - Runs unit tests with coverage
   - Runs integration tests with coverage
   - Uploads coverage to Codecov
   - ⚠️ **Might fail** - Requires proper test setup

4. **Docker** (Lines 186-227)
   - Builds dev + prod Docker images
   - Runs Trivy vulnerability scanner
   - ✅ **Should pass** - exit-code: 0 for Trivy

### Workflow: `.github/workflows/build.yml`

**Requirements:**
- GCP_PROJECT_ID secret
- GCP_SA_KEY secret
- Docker build must succeed
- ⚠️ **Will fail** - Missing GCP secrets

### Workflow: `.github/workflows/deploy.yml`

**Requirements:**
- Workload Identity Provider
- Service account authentication
- Neon database secrets
- API key secrets (OPENAI, ANTHROPIC)
- ⚠️ **Will fail** - Missing secrets + infrastructure

---

## Action Plan

### Phase 1: Get CI Badge Green (Core Quality) ✅ Highest Priority

This is the most important badge - it shows code quality and test coverage.

#### Step 1.1: Verify mypy passes locally
```bash
source .venv/bin/activate
mypy src/
```
**Expected:** Should pass with current overrides in pyproject.toml

#### Step 1.2: Run tests locally
```bash
source .venv/bin/activate

# Option 1: If you have PostgreSQL + Redis running locally
pytest tests/unit -v
pytest tests/integration -v

# Option 2: Use docker-compose for services
docker-compose up -d postgres redis
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/copy_that_test"
export REDIS_URL="redis://localhost:6379/0"
alembic upgrade head
pytest tests/ -v
```

#### Step 1.3: Configure GitHub Secrets

Navigate to: https://github.com/joshband/copy-that/settings/secrets/actions

**Required secrets:**
1. **CODECOV_TOKEN** (Priority 1)
   - Get from: https://codecov.io/gh/joshband/copy-that/settings
   - Sign up for free Codecov account if needed
   - Add repository to Codecov
   - Copy token from Settings

2. **NEON_DATABASE_URL** (Priority 1 - for CI tests)
   - Format: `postgresql+asyncpg://user:pass@host/dbname`
   - Can use existing Neon database or create test DB
   - Should be a separate test database, not production

3. **APP_SECRET_KEY** (Priority 2)
   - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

4. **OPENAI_API_KEY** (Priority 3 - if tests need it)
   - From: https://platform.openai.com/api-keys

5. **ANTHROPIC_API_KEY** (Priority 3 - if tests need it)
   - From: https://console.anthropic.com/settings/keys

#### Step 1.4: Push trigger and verify CI

```bash
# Make a small change to trigger CI
git commit --allow-empty -m "ci: Trigger CI workflow to verify green status"
git push origin main

# Monitor at: https://github.com/joshband/copy-that/actions
```

**Success Criteria:**
- ✅ Security job passes (or shows informational warnings)
- ✅ Lint job passes (mypy respects overrides)
- ✅ Test job passes (all tests green)
- ✅ Docker job passes (builds successfully)
- ✅ Codecov badge shows coverage percentage

---

### Phase 2: Get Build Badge Green (Optional) 🟡 Medium Priority

This requires GCP infrastructure setup.

#### Step 2.1: Create GCP Project (if not exists)

```bash
# Set project ID
export GCP_PROJECT_ID="copy-that-platform"

# Create project
gcloud projects create $GCP_PROJECT_ID

# Set billing account (required)
gcloud beta billing projects link $GCP_PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

#### Step 2.2: Create Service Account

```bash
# Create service account for GitHub Actions
gcloud iam service-accounts create copy-that-cloudbuild \
  --display-name="Copy That CloudBuild" \
  --project=$GCP_PROJECT_ID

# Grant permissions
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:copy-that-cloudbuild@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account=copy-that-cloudbuild@${GCP_PROJECT_ID}.iam.gserviceaccount.com
```

#### Step 2.3: Create Artifact Registry

```bash
# Enable API
gcloud services enable artifactregistry.googleapis.com \
  --project=$GCP_PROJECT_ID

# Create repository
gcloud artifacts repositories create copy-that \
  --repository-format=docker \
  --location=us-central1 \
  --project=$GCP_PROJECT_ID
```

#### Step 2.4: Configure GitHub Secrets

Add to: https://github.com/joshband/copy-that/settings/secrets/actions

1. **GCP_PROJECT_ID**
   - Value: `copy-that-platform` (or your project ID)

2. **GCP_SA_KEY**
   - Value: Contents of `key.json` file
   - Format: JSON string with service account credentials

---

### Phase 3: Get Deploy Badge Green (Optional) 🔵 Low Priority

This requires Cloud Run setup and is optional for development.

**Requirements:**
- Workload Identity Provider (Recommended over service account keys)
- Cloud Run services created
- Cloud Run jobs for migrations
- Environment secrets

**Recommendation:** Skip for now, focus on CI badge first.

---

## Quick Win Strategy

**Focus on Phase 1 only** - Get the CI badge green:

1. **Immediate (5 minutes):**
   - Sign up for Codecov: https://codecov.io/
   - Add repo to Codecov
   - Copy CODECOV_TOKEN to GitHub Secrets

2. **Short-term (30 minutes):**
   - Create Neon test database
   - Add DATABASE_URL to GitHub Secrets
   - Generate APP_SECRET_KEY, add to GitHub Secrets

3. **Test (10 minutes):**
   - Run `mypy src/` locally (verify passes)
   - Run `pytest tests/unit` locally (verify passes)
   - Run `ruff check .` locally (verify passes)

4. **Deploy (5 minutes):**
   - Push empty commit to trigger CI
   - Monitor GitHub Actions
   - Verify CI badge turns green

**Total time: ~50 minutes to get CI badge green**

---

## Troubleshooting

### mypy fails in CI but passes locally

**Cause:** Different Python/mypy versions
**Fix:** Check CI uses Python 3.12 (it does, line 65)

### Tests fail in CI but pass locally

**Possible causes:**
1. Missing environment variables
2. Database migrations not run
3. Test dependencies missing

**Debug:**
- Check Actions logs
- Verify DATABASE_URL format
- Ensure `alembic upgrade head` runs before tests (line 139)

### Codecov upload fails

**Cause:** Missing CODECOV_TOKEN
**Fix:** Add token to GitHub Secrets (see Step 1.3.1)

### Docker build fails

**Possible causes:**
1. Dockerfile syntax error
2. Missing dependencies
3. Build context issues

**Debug:**
- Test locally: `docker build -t copy-that:test .`
- Check Dockerfile exists at repo root
- Verify requirements.txt or pyproject.toml exists

---

## Success Metrics

**Phase 1 Complete:**
- ✅ CI badge shows green
- ✅ Codecov badge shows coverage %
- ✅ All 4 CI jobs pass
- ✅ Test coverage > 80%

**Phase 2 Complete:**
- ✅ Build badge shows green
- ✅ Docker images published to GCP

**Phase 3 Complete:**
- ✅ Deploy badge shows green
- ✅ Staging environment live
- ✅ Production environment live

---

## Cost Estimate

**Free Tier:**
- GitHub Actions: 2,000 minutes/month (free for public repos)
- Codecov: Free for public repos
- Total: $0/month

**Paid Services (Optional - Phase 2/3):**
- GCP Artifact Registry: $0.10/GB/month (~$0.50/month)
- GCP Cloud Run: Pay per use (~$5-10/month for low traffic)
- Neon Database: Free tier (3GB, sufficient for testing)
- Total: ~$5-10/month (only if Phase 2/3 enabled)

**Recommendation:** Start with Phase 1 (free), add Phase 2/3 later if needed.

---

## Next Steps

1. **Review this plan** - Understand each phase
2. **Choose strategy:**
   - **Quick Win:** Phase 1 only (~50 min, $0)
   - **Full Setup:** All phases (~4 hours, ~$10/month)
3. **Execute Phase 1:**
   - Configure Codecov token
   - Configure database secrets
   - Push and verify
4. **Celebrate green badges!** 🎉

---

## References

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Codecov Docs](https://docs.codecov.com/docs)
- [GCP Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [GCP Cloud Run](https://cloud.google.com/run/docs)
- [Neon Database](https://neon.tech/docs/introduction)

---

**Last Updated:** 2025-12-12
**Status:** Ready for execution - Start with Phase 1
