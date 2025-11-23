# GitHub Environments Setup

This guide explains how to set up GitHub environments for the tiered testing and deployment strategy.

## Overview

| Environment | Branch/Trigger | Test Tier | Purpose |
|-------------|----------------|-----------|---------|
| (none) | PR, fix/* | Light | Fast feedback, lint/type/fast-unit |
| (none) | feature/*, develop | Medium | Full tests before merge |
| staging | develop merge | Medium | Deploy & test in GCP staging |
| production | v* tags | Heavy | Full suite, deploy to GCP prod |

## Test Tiers

### Light (Default for PRs)
- Ruff lint/format
- MyPy type check
- Fast unit tests (excludes `@pytest.mark.slow`)

**Runtime:** ~2-3 minutes

### Medium (Feature branches, develop, main)
- All light tests
- Full unit tests with coverage
- Integration tests with DB/Redis

**Runtime:** ~5-8 minutes

### Heavy (Releases, tags)
- All medium tests
- Security scanning (pip-audit, bandit, gitleaks)
- E2E tests with Playwright
- Docker build + Trivy scan
- Performance benchmarks (when added)

**Runtime:** ~15-20 minutes

## GitHub Environment Setup

### 1. Create Environments

Go to **Settings → Environments** and create:

#### `staging`
- **Deployment branches:** `develop`
- **Required reviewers:** (optional, 0 for auto-deploy)
- **Wait timer:** 0 minutes

#### `production`
- **Deployment branches:** Only tags matching `v*`
- **Required reviewers:** 1-2 team members
- **Wait timer:** 5 minutes (optional pause before deploy)

### 2. Add Environment Secrets

For each environment, add:

```
# GCP Credentials
GCP_PROJECT_ID=your-project-id
GCP_SA_KEY=<base64-encoded-service-account-key>

# Database (environment-specific)
DATABASE_URL=postgresql+asyncpg://...

# Redis
REDIS_URL=redis://...

# API Keys (if different per environment)
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

### 3. Branch Protection Rules

Go to **Settings → Branches** and add rules:

#### `main`
- ✅ Require pull request before merging
- ✅ Require status checks: `lint`, `type-check`, `unit-tests-fast`
- ✅ Require branches to be up to date

#### `develop`
- ✅ Require pull request before merging
- ✅ Require status checks: `lint`, `type-check`, `unit-tests-fast`

## Using Test Tier Labels

Override the automatic tier detection with PR labels:

- `test:light` - Only run light tests (emergency hotfixes)
- `test:medium` - Run medium tests
- `test:heavy` - Run full test suite (before major merges)

## Branch Naming Convention

The workflow automatically selects test tiers based on branch names:

| Pattern | Tier | Use Case |
|---------|------|----------|
| `fix/*`, `hotfix/*` | light | Bug fixes |
| `docs/*` | light | Documentation only |
| `feature/*` | medium | New features |
| `release/*` | heavy | Release preparation |
| `main` | medium | Main branch |
| `develop` | medium | Development branch |
| `v*` (tags) | heavy | Production releases |

## Workflow Files

- **ci-tiered.yml** - Main tiered testing workflow
- **ci.yml** - Legacy workflow (can be deprecated)

## GCP Deployment (TODO)

The deploy jobs currently have placeholder steps. To implement:

### Staging Deployment
```yaml
- name: Authenticate to GCP
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}

- name: Deploy to Cloud Run
  uses: google-github-actions/deploy-cloudrun@v2
  with:
    service: copy-that-staging
    region: us-central1
    image: gcr.io/${{ secrets.GCP_PROJECT_ID }}/copy-that:${{ github.sha }}
```

### Production Deployment
```yaml
- name: Deploy to Cloud Run
  uses: google-github-actions/deploy-cloudrun@v2
  with:
    service: copy-that-production
    region: us-central1
    image: gcr.io/${{ secrets.GCP_PROJECT_ID }}/copy-that:${{ github.ref_name }}
```

## Monitoring Deployments

After setup, you can:
1. View deployment history in **Actions → Deployments**
2. See environment status on the repo homepage
3. Require approvals before production deploys

## Cost Optimization

This tiered approach reduces CI costs by:
- Running only fast tests for small PRs (~60% of PRs)
- Reserving expensive tests (E2E, security, Docker) for releases
- Using GitHub's concurrency settings to cancel duplicate runs
