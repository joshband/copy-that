# GCP Cloud Run (consolidated)

**Last Updated:** 2026-09-21  
**Supersedes:** archived `gcp_terraform_deployment.md`, `DEPLOYMENT_GUIDE_GCP_CLOUDRUN.md`, `production_deployment_guide.md`, `infrastructure_setup.md` in `~/Documents/copy-that-archive/setup-history/`.

---

## Target shape

```
Internet → Cloud Run (FastAPI) → Neon Postgres
                              → Upstash / Redis (optional Celery)
         Artifact Registry (images)
         Secret Manager (keys)
Frontend: separate static host or Cloud Run
```

---

## Prerequisites

1. GCP project + billing  
2. `gcloud` CLI + Terraform  
3. Docker  
4. Neon (or Cloud SQL) connection string  
5. Secrets: `ANTHROPIC_API_KEY`, `SECRET_KEY`, DB URL, etc. (never commit)  

---

## Outline

```bash
# Auth
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# Build & push API image (adjust region/repo)
docker build -f Dockerfile -t copy-that-api:latest .
gcloud auth configure-docker REGION-docker.pkg.dev
docker tag copy-that-api:latest \
  REGION-docker.pkg.dev/PROJECT/copy-that/copy-that-api:latest
docker push REGION-docker.pkg.dev/PROJECT/copy-that/copy-that-api:latest

# Terraform (paths vary — prefer deploy/terraform or terraform/ as in-repo)
cd deploy/terraform   # or terraform/ — see repo layout
terraform init
terraform plan
terraform apply
```

Configure Cloud Run env from Secret Manager; health check `/health`.  
Disable unauthenticated invoke for staging/prod unless intentionally public.

---

## Validate before deploy

```bash
pnpm type-check
make test-quick
# optional: make check
```

---

## Related

- Comparison: [deployment_options.md](./deployment_options.md)  
- Local: [start_here.md](./start_here.md)  
- Ops: [../ops/runbook.md](../ops/runbook.md)  
- Note: root `terraform/DEPRECATED.md` may point at older paths — prefer this doc + live `deploy/` tree.
