# API_CONTRACTS.md
# API Contracts & Versioning

This document defines **explicit API expectations** between backend, frontend,
and external consumers.

---

## Versioning Strategy
- `/api/v1` is stable
- Breaking changes require `/api/v2`

---

## Core Endpoints
- `POST /extract`
- `GET /projects`
- `GET /tokens`

---

## Error Semantics
- 400: validation error
- 401: auth failure
- 429: rate limit exceeded
- 500: internal error

---

## Contract Enforcement
- OpenAPI snapshots generated in CI
- Frontend validated against schema
- Breaking changes fail CI

---
