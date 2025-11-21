# Frontend Setup Guide

**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Complete

Complete guide to setting up and running the Copy That React frontend.

---

## 📋 Prerequisites

- **Node.js** 18+ (20+ recommended)
- **npm** or **pnpm** (pnpm 8+ recommended for speed)
- **Git** for version control
- Copy That repository cloned

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies (pnpm is 10-100x faster than npm)
pnpm install
# or: npm install

# 3. Create environment file
cp .env.example .env.local

# 4. Start development server
pnpm dev
# or: npm run dev

# 5. Open in browser
open http://localhost:5173
```

**Result:** Frontend running on http://localhost:5173 with hot reload enabled ✅

---

## 📁 Directory Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── ColorTokenCard.tsx
│   │   ├── TokenList.tsx
│   │   └── ExtractForm.tsx
│   │
│   ├── pages/                # Page components
│   │   ├── ExtractPage.tsx
│   │   ├── ProjectsPage.tsx
│   │   └── NotFoundPage.tsx
│   │
│   ├── hooks/                # Custom React hooks
│   │   ├── useTokens.ts
│   │   └── useExtraction.ts
│   │
│   ├── types/                # TypeScript type definitions
│   │   ├── tokens.ts
│   │   ├── api.ts
│   │   └── generated/        # Auto-generated types
│   │
│   ├── api/                  # API client
│   │   ├── client.ts
│   │   ├── endpoints.ts
│   │   └── interceptors.ts
│   │
│   ├── styles/               # Global styles
│   │   ├── globals.css
│   │   └── tailwind.css
│   │
│   ├── utils/                # Utility functions
│   │   ├── formatting.ts
│   │   ├── validation.ts
│   │   └── transforms.ts
│   │
│   ├── App.tsx               # Main app component
│   └── main.tsx              # Entry point
│
├── public/                   # Static assets
│   └── images/
│
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
├── package.json              # Dependencies
└── .env.example              # Environment template
```

---

## 🔧 Environment Configuration

### .env.local

Create `.frontend/.env.local` with:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_EXPERIMENTAL_FEATURES=false

# Deployment
VITE_APP_ENV=development
```

### Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `VITE_API_URL` | Backend API endpoint | `http://localhost:8000` |
| `VITE_API_TIMEOUT` | Request timeout (ms) | `30000` |
| `VITE_ENABLE_DEBUG` | Show debug logging | `true` |
| `VITE_ENABLE_EXPERIMENTAL_FEATURES` | Enable beta features | `false` |
| `VITE_APP_ENV` | Environment name | `development` \| `staging` \| `production` |

---

## 🎨 Tech Stack

### Core Framework
- **React 18** - UI framework
- **Vite 5** - Build tool (10-100x faster than Webpack)
- **TypeScript** - Type safety

### Styling
- **Tailwind CSS** - Utility-first CSS
- **CSS Modules** - Component-scoped styles

### HTTP Client
- **Fetch API** - Built-in, no dependencies
- Custom client in `src/api/client.ts`

### Type Generation
- **Zod** - Runtime validation
- **zod-to-openapi** - Generate OpenAPI from Zod

### Testing
- **Vitest** - Unit tests
- **React Testing Library** - Component tests
- **Playwright** - E2E tests

---

## 🔌 API Client Setup

### Overview

The API client abstracts HTTP calls to the backend:

```typescript
// src/api/client.ts
import { ApiClient } from './client';

export const apiClient = new ApiClient({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: import.meta.env.VITE_API_TIMEOUT
});
```

### Making API Calls

```typescript
import { apiClient } from '@/api/client';

// GET request
const colors = await apiClient.get('/api/v1/jobs/1/colors');

// POST request
const job = await apiClient.post('/api/v1/jobs', {
  project_id: 1,
  source_url: 'image.jpg',
  extraction_type: 'color'
});

// Error handling
try {
  const colors = await apiClient.get('/api/v1/jobs/1/colors');
} catch (error) {
  console.error('Failed to fetch colors:', error);
}
```

### Interceptors

The API client includes interceptors for:

```typescript
// Request interceptor (adds auth token if needed)
apiClient.interceptors.request.use((config) => {
  // Add authorization header
  config.headers['Authorization'] = `Bearer ${getAuthToken()}`;
  return config;
});

// Response interceptor (handles errors globally)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      redirectToLogin();
    }
    return Promise.reject(error);
  }
);
```

---

## 🪝 Custom Hooks

### useTokens - Fetch tokens from API

```typescript
import { useTokens } from '@/hooks/useTokens';

function ColorDisplay() {
  const { colors, loading, error } = useTokens('colors', jobId);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {colors.map(color => (
        <ColorCard key={color.id} color={color} />
      ))}
    </div>
  );
}
```

### useExtraction - Upload and extract tokens

```typescript
import { useExtraction } from '@/hooks/useExtraction';

function ExtractForm() {
  const { extracting, extractTokens } = useExtraction();

  async function handleFileUpload(file: File) {
    const tokens = await extractTokens(file, 'color');
    console.log('Extracted:', tokens);
  }

  return (
    <input
      type="file"
      onChange={(e) => handleFileUpload(e.target.files[0])}
      disabled={extracting}
    />
  );
}
```

---

## 📦 Available Scripts

### Development

```bash
# Start dev server with hot reload
pnpm dev

# Type checking
pnpm typecheck

# Lint code
pnpm lint

# Format code
pnpm format
```

### Testing

```bash
# Run all tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run tests with coverage
pnpm test:coverage

# E2E tests
pnpm test:e2e
```

### Building

```bash
# Production build
pnpm build

# Preview production build locally
pnpm preview

# Build analysis (check bundle size)
pnpm build:analyze
```

---

## 🧪 Component Examples

### Simple Component

```typescript
// src/components/ColorTokenCard.tsx
import React from 'react';
import { ColorToken } from '@/types/tokens';

interface Props {
  token: ColorToken;
}

export function ColorTokenCard({ token }: Props) {
  const percentConfidence = Math.round(token.confidence * 100);

  return (
    <div className="rounded-lg border border-gray-200 p-4">
      <div
        className="h-12 w-12 rounded"
        style={{ backgroundColor: token.hex }}
      />
      <div className="mt-2">
        <h3 className="font-semibold">{token.hex}</h3>
        {token.semantic_name && (
          <p className="text-sm text-gray-600">{token.semantic_name}</p>
        )}
        <p className="mt-1 text-xs">
          {percentConfidence}% confident
        </p>
      </div>
    </div>
  );
}
```

### Component with Data Fetching

```typescript
// src/components/TokenList.tsx
import React, { useEffect, useState } from 'react';
import { apiClient } from '@/api/client';
import { ColorTokenCard } from './ColorTokenCard';

interface Props {
  jobId: number;
}

export function TokenList({ jobId }: Props) {
  const [tokens, setTokens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchTokens() {
      try {
        const response = await apiClient.get(
          `/api/v1/jobs/${jobId}/colors`
        );
        setTokens(response.data.colors);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    }

    fetchTokens();
  }, [jobId]);

  if (loading) return <div>Loading tokens...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="grid grid-cols-4 gap-4">
      {tokens.map(token => (
        <ColorTokenCard key={token.id} token={token} />
      ))}
    </div>
  );
}
```

---

## 🛂 TypeScript Setup

### Type Generation from Backend

Types are auto-generated from backend schemas:

```bash
# Generate types from backend OpenAPI
pnpm generate:types

# This creates:
# - src/types/generated/color.ts
# - src/types/generated/spacing.ts
# - etc.
```

### Using Generated Types

```typescript
import { ColorTokenAPISchema } from '@/types/generated/color';

async function extractColors(): Promise<ColorTokenAPISchema[]> {
  const response = await apiClient.post('/api/v1/extract/color', {
    image: imageData
  });
  return response.data; // Type-safe!
}
```

---

## 🎨 Styling

### Tailwind CSS

```typescript
// Use Tailwind classes
<div className="flex items-center justify-between rounded-lg border p-4">
  <h2 className="text-lg font-semibold">Colors</h2>
  <button className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600">
    Export
  </button>
</div>
```

### CSS Modules

```typescript
// src/components/Special.module.css
.cardWrapper {
  border: 2px solid var(--primary-color);
  padding: 1rem;
}

// src/components/Special.tsx
import styles from './Special.module.css';

export function Special() {
  return <div className={styles.cardWrapper}>...</div>;
}
```

---

## 🔍 Debugging

### React DevTools

Install browser extension:
- [Chrome](https://chrome.google.com/webstore/detail/react-developer-tools)
- [Firefox](https://addons.mozilla.org/firefox/addon/react-devtools/)

### Console Logging

```typescript
// Debug API calls
if (import.meta.env.VITE_ENABLE_DEBUG) {
  console.log('API Request:', url, config);
  console.log('API Response:', response.data);
}
```

### Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Make API call
4. See request/response details
5. Check timing and payload

---

## 🚀 Deployment

### Build for Production

```bash
# Create optimized production build
pnpm build

# Result: dist/ folder with optimized assets
```

### Environment-Specific Builds

```bash
# Staging build
VITE_APP_ENV=staging pnpm build

# Production build
VITE_APP_ENV=production pnpm build
```

### Serving Static Files

Once built, serve the `dist/` folder:

```bash
# Local preview
pnpm preview

# Or deploy dist/ to any static host:
# - Vercel
# - Netlify
# - GitHub Pages
# - Cloud Storage + CDN
```

---

## 🐛 Troubleshooting

### Issue: "Cannot find module '@/api/client'"

**Solution:** Check `tsconfig.json` has correct path alias:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### Issue: API calls failing with 404

**Solution:** Verify `VITE_API_URL` in `.env.local`:
```bash
# Check backend is running
curl http://localhost:8000/api/v1/db-test

# Update .env.local if needed
VITE_API_URL=http://localhost:8000
```

### Issue: TypeScript errors on imported types

**Solution:** Regenerate types from backend:
```bash
pnpm generate:types
```

### Issue: Slow development server startup

**Solution:** Use pnpm instead of npm (10-100x faster):
```bash
pnpm install
pnpm dev
```

---

## 📚 Related Documentation

- **setup/start_here.md** - Quick navigation
- **workflows/phase_4_color_vertical_slice.md** - Week 1 implementation (includes frontend)
- **api_reference.md** - Backend API endpoints
- **testing/testing_overview.md** - Frontend testing strategies

---

**Version:** 1.0 | **Last Updated:** 2025-11-19 | **Status:** Complete
