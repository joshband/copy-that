# ROADMAP_06.md
# CI/CD, Security, and Operational Hardening (Code-Informed)

This roadmap continuation incorporates findings from the actual GitHub Actions workflows,
runtime configuration, and deployment practices. Items are sequenced to reduce risk first,
then improve velocity and correctness.

---

## 1. Consolidate CI into a Single Source of Truth (High Priority)

### Context
You currently operate overlapping CI pipelines (`ci.yml` and `ci-tiered.yml`), both executing
on pushes and PRs with partially duplicated responsibilities. This increases cost, risk of drift,
and ambiguity in branch protection configuration.

### Claude-friendly Issue
Refactor GitHub Actions so **`ci-tiered.yml` becomes the canonical CI pipeline**.
Either remove `ci.yml` entirely or restrict it to scheduled, non-blocking jobs
(e.g. dependency audits, nightly checks).

Tasks:
- Identify overlapping jobs between `ci.yml` and `ci-tiered.yml`
- Remove or disable redundant workflows
- Update branch protection rules to reference the new canonical checks
- Document CI tiers and intended triggers in `docs/`

### Acceptance Criteria
- Only one workflow enforces PR validation
- Branch protections match actual CI jobs
- CI runtime and duplicate job execution reduced

---

## 2. Make Staging Migrations Mandatory (High Priority)

### Context
The deploy workflow allows staging database migrations to fail without blocking deploys.
This can produce “green” deploys with broken staging environments.

### Claude-friendly Issue
Update the deployment workflow so **staging migrations are mandatory**.
If migrations fail, the deployment must fail.

Tasks:
- Remove `continue-on-error` from staging migration steps
- Ensure migration logs are surfaced clearly in workflow output
- Optionally add rollback or notification hooks

### Acceptance Criteria
- Staging deploy fails if migrations fail
- Schema is always up to date post-deploy
- Clear failure signal and logs are visible in CI

---

## 3. Secure Cloud Run Services (High Priority)

### Context
Both staging and production deployments currently allow unauthenticated access.
This is risky given API cost exposure and proprietary extraction logic.

### Claude-friendly Issue
Remove `--allow-unauthenticated` from Cloud Run deployments.
Implement a default authentication strategy.

Options:
- API key enforcement (already implied in `.env.example`)
- IAM-based auth for internal services
- IAP for protected access

Tasks:
- Decide on auth strategy per environment
- Update deploy workflow flags
- Adjust health checks and CORS config
- Update documentation

### Acceptance Criteria
- Cloud Run rejects unauthenticated requests by default
- Health checks continue to function
- Auth flow documented for local, staging, and prod

---

## 4. Standardize on Workload Identity for GCP Auth (Medium Priority)

### Context
Build workflows use long-lived service account keys, while deploy workflows use
OIDC Workload Identity. This is inconsistent and less secure.

### Claude-friendly Issue
Migrate **all GCP auth in CI** to Workload Identity.
Remove service account key JSON secrets.

Tasks:
- Update build workflows to use `google-github-actions/auth@v3`
- Remove `GCP_SA_KEY` usage
- Tighten IAM permissions for the GitHub identity

### Acceptance Criteria
- No GCP service account key secrets remain
- Builds and pushes still succeed
- IAM roles documented and minimal

---

## 5. Decide Fate of Neon PR Preview Databases (Medium Priority)

### Decision
Removed the Neon preview DB workflow (it was not wired into CI/tests). If we need preview DBs
later, reintroduce with full CI integration (migrations + schema diff + PR comment).

### Current State
- `.github/workflows/neon_workflow.yml` removed
- CI/tests use existing DATABASE_URL (local/Neon main) as before
- Docs updated to reflect removal

### Acceptance Criteria
- No unused Neon preview automation remains
- Documentation reflects the removal and future intent

---

## 6. Clarify CI vs Deploy Ownership (Medium Priority)

### Decision
CI validates only. Deployments live exclusively in `deploy.yml`. Removed placeholder deploy
jobs from `ci-tiered.yml` to avoid ambiguity.

### Acceptance Criteria
- One clear deployment path (`deploy.yml`)
- No placeholder or misleading deploy steps in CI
- Documentation reflects reality

## 7. Concurrency & Memory Limits (Performance)

### Decision
Add explicit concurrency/memory controls:
- API extraction endpoints use a global semaphore (`EXTRACTION_MAX_CONCURRENCY`, default 4)
- Payload size limit for base64 uploads (`EXTRACTION_MAX_IMAGE_BYTES`, default 5MB) returns 413
- Cloud Run concurrency default reduced to 20 via Terraform variable

### Acceptance Criteria
- Predictable degradation under load; fewer OOMs
- Limits configurable via env/terraform and documented

### Acceptance Criteria
- One clear deployment path exists
- No placeholder or misleading deploy steps
- Docs reflect reality

---

## 7. Align Env Configuration with Runtime Enforcement (Lower Priority)

### Context
`.env.example` defines many knobs (rate limiting, auth, tenancy) that are not
uniformly enforced or validated at runtime.

### Claude-friendly Issue
Audit environment configuration and enforce critical settings at startup.

Tasks:
- Validate required env vars on app startup
- Fail fast on missing security-critical config
- Document environment-specific defaults

### Acceptance Criteria
- App fails fast on invalid config
- Security-sensitive settings enforced
- Docs match runtime behavior

---

## Suggested Execution Order

1. CI consolidation
2. Staging migration enforcement
3. Cloud Run authentication
4. GCP auth standardization
5. Neon preview DB decision
6. CI vs deploy ownership cleanup
7. Env config enforcement

---

## Outcome

After completing this roadmap slice:
- CI is simpler, cheaper, and authoritative
- Deployments are safer and more predictable
- Security posture is materially improved
- Infra complexity matches actual usage
