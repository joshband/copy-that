# OPERATIONS.md
# Copy That – Operations Guide

This document explains **how to run, deploy, and debug** Copy That.

---

## Environments
- **Local:** Docker Compose, local Redis, local storage
- **Staging:** Cloud Run, Neon branch, limited auth
- **Production:** Cloud Run, Neon main branch, strict auth

---

## Deployment Flow
1. Commit merged to main
2. CI passes (tiered)
3. Build workflow produces image
4. Deploy workflow applies migrations
5. Cloud Run revision updated

---

## Database Operations
- All schema changes go through Alembic
- Never modify schema manually in prod
- Use Neon branches for risky migrations

---

## Background Jobs
- Celery workers handle batch extraction
- Retries are bounded
- Failures logged and surfaced in metrics

---

## Observability
- Prometheus metrics for latency and throughput
- Structured logs in Cloud Run
- Alerts for error rates and cost anomalies

---
