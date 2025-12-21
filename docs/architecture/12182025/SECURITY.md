# SECURITY.md
# Copy That – Security Model

This document describes the **security posture and threat model**.

---

## Authentication
- API keys for programmatic access
- OAuth for SaaS users
- IAM for internal services

---

## Authorization
- Tenant isolation enforced at data layer
- No cross‑tenant queries permitted

---

## Data Handling
- Uploaded images treated as sensitive
- Storage is environment‑scoped
- Retention policies configurable

---

## Secrets
- Stored in GCP Secret Manager
- Never committed to repo
- Rotated periodically

---
