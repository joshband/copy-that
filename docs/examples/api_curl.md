# API Examples (curl)

Assumptions:

- Base URL: `http://localhost:8000`
- Content-Type: `application/json` (or multipart where noted)
- Prefer UI at http://localhost:5173 for first extract; curl below for automation

Health / docs:

```bash
curl -s http://localhost:8000/health
# OpenAPI UI: http://localhost:8000/docs
```

---

## Projects (required for most extracts)

Create a project and capture `id` as `project_id`:

```bash
curl -s -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo Project","description":"MVP extract demo"}'
# → {"id":1, ...}
```

List:

```bash
curl -s http://localhost:8000/api/v1/projects
```

---

## MVP extracts

### Colors

```bash
curl -s -X POST http://localhost:8000/api/v1/colors/extract \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "image_url": "https://example.com/image.jpg",
    "max_colors": 10
  }'
```

### Spacing

```bash
curl -s -X POST http://localhost:8000/api/v1/spacing/extract \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1, "image_url": "https://example.com/image.jpg"}'
```

### Shadows

```bash
curl -s -X POST http://localhost:8000/api/v1/shadows/extract \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1, "image_url": "https://example.com/image.jpg"}'
```

### Design tokens export (W3C / CSS)

```bash
curl -s "http://localhost:8000/api/v1/design-tokens/export/w3c?project_id=1"
curl -s "http://localhost:8000/api/v1/design-tokens/export/css?project_id=1"
```

Interactive catalog: http://localhost:8000/docs

---

## Multi-extract (mounted, demo / alt path)

`POST /api/v1/extract/...` is registered for demos/ops (SSE multi-family). Prefer per-family MVP routes or the UI for the happy path. See [CURRENT_ARCHITECTURE_STATE.md](../architecture/CURRENT_ARCHITECTURE_STATE.md).

---

## Sessions & libraries (parked P5)

Mounted but **not** the MVP happy path. Libraries / curation / batch session extract are P5. Use only for experiments:

```bash
# Parked — not required for MVP extract → tabs → export
curl -s -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1, "name": "Brand Sweep", "description": "Batch of hero images"}'
```

Export / curate library endpoints under `/api/v1/sessions/{id}/…` are likewise P5.
