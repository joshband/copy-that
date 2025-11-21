# Batch Extraction Example

Minimal end-to-end example using `BatchColorExtractor` and the session endpoints.

## 1) Create a session
```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "name": "Brand Collateral Sweep",
    "description": "Batch of hero banners"
  }'
```

## 2) Batch extract
```bash
curl -X POST http://localhost:8000/api/v1/sessions/1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": [
      "https://example.com/hero1.jpg",
      "https://example.com/hero2.jpg",
      "https://example.com/hero3.jpg"
    ],
    "max_colors": 12
  }'
```

Expected response (shape):
```json
{
  "status": "success",
  "session_id": 1,
  "library_id": 1,
  "extracted_tokens": 24,
  "statistics": {
    "color_count": 24,
    "image_count": 3,
    "avg_confidence": 0.93,
    "dominant_colors": ["#FF5733", "#0066FF", "..."],
    "multi_image_colors": 8
  }
}
```

## 3) Inspect the library
```bash
curl http://localhost:8000/api/v1/sessions/1/library
```

## 4) Export the library
```bash
curl "http://localhost:8000/api/v1/sessions/1/library/export?format=w3c"
```

## Notes (from `BatchColorExtractor`)
- Concurrency limit: 3 (default) — adjust in code if needed.
- Deduplication: Delta-E threshold default `2.0` (JND); lower = stricter, higher = more merging.
- Provenance: Each aggregated token tracks source images and confidences; persisted to `color_tokens.provenance`.
- Persistence: Tokens are stored with `library_id` and `project_id` for audit/export.
