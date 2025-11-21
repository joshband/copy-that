# API Examples (curl)

Assumptions:
- Base URL: `http://localhost:8000`
- Content-Type: `application/json`
- No auth required (add `Authorization: Bearer ...` if you introduce auth later).

## Projects

Create a project
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo Project","description":"Color extraction demo"}'
```

List projects
```bash
curl http://localhost:8000/api/v1/projects
```

## Color Extraction

Extract from image URL
```bash
curl -X POST http://localhost:8000/api/v1/colors/extract \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "image_url": "https://example.com/image.jpg",
    "max_colors": 10
  }'
```

Manually create a color token
```bash
curl -X POST http://localhost:8000/api/v1/colors \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "hex": "#FF5733",
    "rgb": "rgb(255,87,51)",
    "name": "Coral Red",
    "design_intent": "primary",
    "confidence": 0.95
  }'
```

Get colors for a project
```bash
curl http://localhost:8000/api/v1/projects/1/colors
```

Get a single color
```bash
curl http://localhost:8000/api/v1/colors/1
```

## Sessions & Libraries

Create an extraction session
```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "name": "Brand Sweep",
    "description": "Batch of hero images"
  }'
```

Batch extract into a session library
```bash
curl -X POST http://localhost:8000/api/v1/sessions/1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": [
      "https://example.com/hero1.jpg",
      "https://example.com/hero2.jpg"
    ],
    "max_colors": 10
  }'
```

Curate roles in a library
```bash
curl -X POST http://localhost:8000/api/v1/sessions/1/library/curate \
  -H "Content-Type: application/json" \
  -d '{
    "role_assignments": [
      {"token_id": 5, "role": "primary"},
      {"token_id": 6, "role": "accent"}
    ],
    "notes": "Primary from hero1, accent from hero2"
  }'
```

Get aggregated library
```bash
curl http://localhost:8000/api/v1/sessions/1/library
```

Export library (format: w3c | css | react | html)
```bash
curl "http://localhost:8000/api/v1/sessions/1/library/export?format=css"
```
