# ⚠️ DEPRECATED - This Terraform Configuration Has Moved

**Date:** 2025-12-12
**Status:** Archived

---

## New Location

All Terraform infrastructure has been consolidated to:

```
deploy/terraform/
```

---

## What Changed

**Old Structure (terraform/):**
- Monolithic main.tf
- Basic Cloud Run setup
- ~10 managed resources

**New Structure (deploy/terraform/):**
- Modular setup (separate .tf files)
- Comprehensive infrastructure:
  - Cloud Run v2 services
  - Artifact Registry
  - VPC networking
  - Workload Identity
  - Secret Manager
  - Neon PostgreSQL (NEW)
- ~25+ managed resources

---

## Migration Instructions

**If you need to reference this old configuration:**

1. **State files preserved in archive:**
   ```
   ~/Documents/copy-that-archive/infrastructure/terraform-legacy/
   ```

2. **Use new configuration:**
   ```bash
   cd deploy/terraform/
   terraform init
   terraform plan
   ```

3. **Documentation updated:**
   - All guides now reference `deploy/terraform/`
   - See: docs/setup/gcp_terraform_deployment.md

---

## DO NOT USE THIS DIRECTORY

This directory is kept only for reference. All active infrastructure is managed from:

```
deploy/terraform/
```

See `deploy/terraform/README.md` for current documentation.
