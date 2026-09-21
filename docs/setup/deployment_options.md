# Deployment options

**Last Updated:** 2026-09-21

| | Local | Minimal cloud | Full cloud |
|---|-------|---------------|------------|
| **Cost** | Free | ~$0–5/mo idle-friendly | Higher (VPC / managed DB) |
| **Best for** | Daily dev | Demo / personal | Production |
| **DB** | Docker Postgres / SQLite | Neon | Cloud SQL or Neon Pro |
| **Redis** | Local | Upstash | Memorystore / Upstash |
| **App** | uvicorn + `pnpm dev` | Cloud Run | Cloud Run + networking |

---

## Local (default)

Follow [start_here.md](./start_here.md): `make db-bootstrap`, uvicorn `:8000`, `pnpm dev`.

Optional: `docker compose up` for supporting services when configured in-repo.

---

## Minimal cloud

Typical pattern: **Cloud Run** API + **Neon** Postgres + **Upstash** Redis + separate frontend host (e.g. Vercel/static).  
Use Terraform under `deploy/` / `terraform/` when present; see [gcp_cloud_run.md](./gcp_cloud_run.md).

---

## Full / production cloud

Private networking, secrets in Secret Manager, IAM/IAP for unauthenticated-off APIs, staging + prod environments.  
Ops notes: [../ops/runbook.md](../ops/runbook.md). Detailed older guides live in `~/Documents/copy-that-archive/setup-history/`.

---

## Choose

1. Developing features → **local**  
2. Sharing a demo URL → **minimal cloud**  
3. Paying customers / compliance → **full cloud** + runbook
