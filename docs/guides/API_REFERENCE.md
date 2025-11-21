# API Reference

**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Complete

Complete reference for Copy That REST API endpoints.

---

## 📚 Base URL

**Development:** `http://localhost:8000`
**Production:** `https://api.copythis.io` (example)

---

## 🏥 Health & Status

### Health Check

Check if API is running:

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Database Test

Test database connectivity:

```http
GET /api/v1/db-test
```

**Response:**
```json
{
  "database": "connected",
  "provider": "Neon",
  "projects_count": 0,
  "message": "Database connection successful! 🎉"
}
```

---

## 📋 Projects

### List Projects

Get all projects:

```http
GET /api/v1/projects
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of projects to skip
- `limit` (int, default: 10) - Number of projects to return

**Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Design System v1",
      "description": "Main design system",
      "created_at": "2025-11-19T10:30:00Z",
      "updated_at": "2025-11-19T10:30:00Z"
    }
  ],
  "total": 1
}
```

### Create Project

Create a new project:

```http
POST /api/v1/projects
Content-Type: application/json

{
  "name": "Design System v2",
  "description": "Updated design system"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Design System v2",
  "description": "Updated design system",
  "created_at": "2025-11-19T11:00:00Z",
  "updated_at": "2025-11-19T11:00:00Z"
}
```

### Get Project

Get specific project:

```http
GET /api/v1/projects/{project_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Design System v1",
  "description": "Main design system",
  "created_at": "2025-11-19T10:30:00Z",
  "updated_at": "2025-11-19T10:30:00Z"
}
```

---

## 💼 Extraction Jobs

### Create Extraction Job

Start a new extraction job:

```http
POST /api/v1/jobs
Content-Type: application/json

{
  "project_id": 1,
  "source_url": "image.jpg",
  "extraction_type": "color"
}
```

**Parameters:**
- `project_id` (int, required) - Project ID
- `source_url` (string, required) - Image URL or path
- `extraction_type` (string, required) - Token type: `color`, `spacing`, `typography`, `all`

**Response:**
```json
{
  "id": 1,
  "project_id": 1,
  "source_url": "image.jpg",
  "extraction_type": "color",
  "status": "processing",
  "created_at": "2025-11-19T11:00:00Z"
}
```

### Get Job Status

Check extraction job status:

```http
GET /api/v1/jobs/{job_id}
```

**Response:**
```json
{
  "id": 1,
  "project_id": 1,
  "source_url": "image.jpg",
  "extraction_type": "color",
  "status": "completed",
  "result_data": {...},
  "error_message": null,
  "created_at": "2025-11-19T11:00:00Z",
  "completed_at": "2025-11-19T11:02:00Z"
}
```

**Status Values:**
- `pending` - Waiting to start
- `processing` - Currently extracting
- `completed` - Finished successfully
- `failed` - Error occurred

---

## 🎨 Color Tokens

### Extract Colors from Image

Upload image and extract color palette:

```http
POST /api/v1/extract/colors
Content-Type: multipart/form-data

file: <binary image data>
project_id: 1
```

**Response:**
```json
{
  "job_id": 1,
  "colors": [
    {
      "id": 1,
      "hex": "#FF6B35",
      "confidence": 0.95,
      "semantic_name": "vibrant-orange",
      "created_at": "2025-11-19T11:00:00Z"
    },
    {
      "id": 2,
      "hex": "#0066CC",
      "confidence": 0.88,
      "semantic_name": "bright-blue",
      "created_at": "2025-11-19T11:00:00Z"
    }
  ]
}
```

### Get Colors from Job

Retrieve colors extracted in a job:

```http
GET /api/v1/jobs/{job_id}/colors
```

**Query Parameters:**
- `confidence_min` (float, default: 0.0) - Minimum confidence threshold
- `limit` (int, default: 100) - Maximum results

**Response:**
```json
{
  "job_id": 1,
  "colors": [
    {
      "id": 1,
      "hex": "#FF6B35",
      "confidence": 0.95,
      "semantic_name": "vibrant-orange",
      "created_at": "2025-11-19T11:00:00Z"
    }
  ]
}
```

### Get Color Detail

Get specific color token:

```http
GET /api/v1/tokens/color/{color_id}
```

**Response:**
```json
{
  "id": 1,
  "hex": "#FF6B35",
  "confidence": 0.95,
  "semantic_name": "vibrant-orange",
  "metadata": {
    "hue": "orange",
    "temperature": "warm",
    "saturation": "vibrant"
  },
  "created_at": "2025-11-19T11:00:00Z"
}
```

---

## 📏 Spacing Tokens

### Extract Spacing

```http
POST /api/v1/extract/spacing
Content-Type: multipart/form-data

file: <binary image data>
project_id: 1
```

**Response:**
```json
{
  "job_id": 2,
  "spacing": [
    {
      "id": 1,
      "value": 8,
      "unit": "px",
      "scale": "xs",
      "confidence": 0.92,
      "semantic_name": "extra-small-padding",
      "created_at": "2025-11-19T11:00:00Z"
    },
    {
      "id": 2,
      "value": 16,
      "unit": "px",
      "scale": "md",
      "confidence": 0.88,
      "semantic_name": "medium-padding",
      "created_at": "2025-11-19T11:00:00Z"
    }
  ]
}
```

### Get Spacing from Job

```http
GET /api/v1/jobs/{job_id}/spacing
```

---

## 🔤 Typography Tokens

### Extract Typography

```http
POST /api/v1/extract/typography
Content-Type: multipart/form-data

file: <binary image data>
project_id: 1
```

**Response:**
```json
{
  "job_id": 3,
  "typography": [
    {
      "id": 1,
      "font_family": "Inter, -apple-system, sans-serif",
      "font_size": 16,
      "font_weight": 400,
      "line_height": 1.5,
      "confidence": 0.85,
      "semantic_name": "body-text",
      "created_at": "2025-11-19T11:00:00Z"
    }
  ]
}
```

---

## 📤 Export Tokens

### Export as CSS Variables

Export extracted tokens as CSS:

```http
GET /api/v1/jobs/{job_id}/export?format=css
```

**Response:**
```css
:root {
  --color-vibrant-orange: #FF6B35;
  --color-bright-blue: #0066CC;
  --spacing-xs: 8px;
  --spacing-md: 16px;
  --font-body: "Inter", -apple-system, sans-serif;
}
```

### Export as JSON

```http
GET /api/v1/jobs/{job_id}/export?format=json
```

**Response:**
```json
{
  "colors": {
    "vibrant-orange": "#FF6B35",
    "bright-blue": "#0066CC"
  },
  "spacing": {
    "xs": 8,
    "md": 16
  },
  "typography": {
    "body": {
      "fontFamily": "Inter, sans-serif",
      "fontSize": 16
    }
  }
}
```

### Export as TypeScript

```http
GET /api/v1/jobs/{job_id}/export?format=typescript
```

**Response:**
```typescript
export const tokens = {
  colors: {
    vibrantOrange: '#FF6B35',
    brightBlue: '#0066CC'
  },
  spacing: {
    xs: 8,
    md: 16
  },
  typography: {
    body: {
      fontFamily: 'Inter, sans-serif',
      fontSize: 16
    }
  }
} as const;
```

### Supported Formats

| Format | Usage |
|--------|-------|
| `css` | CSS variables |
| `json` | W3C Design Tokens JSON |
| `typescript` | TypeScript object |
| `tailwind` | Tailwind config |
| `material` | Material-UI theme |
| `figma` | Figma design tokens |

---

## 🔍 Search & Filter

### Search Tokens

Search all tokens by name or value:

```http
GET /api/v1/tokens/search?q=orange&type=color
```

**Query Parameters:**
- `q` (string) - Search term
- `type` (string) - Filter by type: `color`, `spacing`, `typography`, etc.
- `project_id` (int) - Filter by project
- `confidence_min` (float) - Minimum confidence

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "type": "color",
      "hex": "#FF6B35",
      "semantic_name": "vibrant-orange",
      "confidence": 0.95
    }
  ],
  "total": 1
}
```

---

## ⚠️ Error Responses

All errors follow this format:

```json
{
  "error": "Error code",
  "message": "Human-readable error message",
  "status": 400
}
```

### Common Errors

| Status | Error | Cause |
|--------|-------|-------|
| 400 | `BAD_REQUEST` | Invalid parameters |
| 401 | `UNAUTHORIZED` | Missing/invalid token |
| 404 | `NOT_FOUND` | Resource doesn't exist |
| 422 | `VALIDATION_ERROR` | Invalid data format |
| 500 | `INTERNAL_SERVER_ERROR` | Server error |

### Example Error

```http
POST /api/v1/projects
Content-Type: application/json

{}  # Missing required fields
```

**Response:**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Validation error: 'name' is required",
  "status": 422,
  "details": [
    {
      "field": "name",
      "message": "required"
    }
  ]
}
```

---

## 🔐 Authentication

**Note:** Currently API is open. In future, add:

```http
GET /api/v1/tokens
Authorization: Bearer {token}
```

---

## 📝 Rate Limiting

**Note:** Not yet implemented. Future limits:
- 100 requests/minute for authenticated users
- 10 requests/minute for unauthenticated requests

---

## 🔄 Webhooks

**Note:** Not yet implemented. Future events:
- `extraction.completed`
- `extraction.failed`
- `token.created`
- `export.generated`

---

## 📖 API Documentation

### Interactive API Docs

After starting the API, visit:

```
http://localhost:8000/docs
```

This provides:
- Swagger UI for testing endpoints
- Request/response schemas
- Try-it-out functionality

---

## 💡 API Client Usage

### Python

```python
import requests

# Extract colors
response = requests.post(
    'http://localhost:8000/api/v1/extract/colors',
    files={'file': open('image.jpg', 'rb')},
    json={'project_id': 1}
)
colors = response.json()['colors']
```

### JavaScript/TypeScript

```typescript
import { apiClient } from './api/client';

// Extract colors
const response = await apiClient.post('/api/v1/extract/colors', {
  file: imageFile,
  project_id: 1
});
const colors = response.data.colors;
```

### curl

```bash
# Create project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "Test"}'

# Extract colors
curl -X POST http://localhost:8000/api/v1/extract/colors \
  -F "file=@image.jpg" \
  -F "project_id=1"

# Get colors from job
curl http://localhost:8000/api/v1/jobs/1/colors
```

---

## 📚 Related Documentation

- **start_here.md** - Quick navigation
- **database_setup.md** - Database structure
- **phase_4_color_vertical_slice.md** - Implementation examples
- **frontend_setup.md** - Frontend API client usage

---

**Version:** 1.0 | **Last Updated:** 2025-11-19 | **Status:** Complete
