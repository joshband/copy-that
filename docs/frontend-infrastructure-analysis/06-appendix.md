# Appendix

> Configuration examples, diagrams, and technical references

---

## Table of Contents

1. [Architecture Diagrams](#architecture-diagrams)
2. [Configuration Examples](#configuration-examples)
3. [Component Examples](#component-examples)
4. [Terraform Examples](#terraform-examples)
5. [CI/CD Examples](#cicd-examples)
6. [File Inventory](#file-inventory)
7. [Glossary](#glossary)

---

## Architecture Diagrams

### Frontend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   App.tsx    │  │   Router     │  │  Providers   │       │
│  │              │◄─┤              │◄─┤  (Query)     │       │
│  └──────┬───────┘  └──────────────┘  └──────────────┘       │
│         │                                                    │
│         ▼                                                    │
│  ┌────────────────────────────────────────────────┐         │
│  │              Component Layer                    │         │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │         │
│  │  │ Session  │  │  Token   │  │  Export  │      │         │
│  │  │ Workflow │  │ Explorer │  │ Manager  │      │         │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘      │         │
│  └───────┼─────────────┼─────────────┼────────────┘         │
│          │             │             │                       │
│          ▼             ▼             ▼                       │
│  ┌────────────────────────────────────────────────┐         │
│  │           State Management (Zustand)           │         │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │         │
│  │  │  Token   │  │    UI    │  │Extraction│      │         │
│  │  │  Store   │  │  Store   │  │  Store   │      │         │
│  │  └──────────┘  └──────────┘  └──────────┘      │         │
│  └────────────────────┬───────────────────────────┘         │
│                       │                                      │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────┐         │
│  │          API Layer (TanStack Query)            │         │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │         │
│  │  │  Hooks   │  │  Client  │  │  Cache   │      │         │
│  │  └──────────┘  └──────────┘  └──────────┘      │         │
│  └────────────────────┬───────────────────────────┘         │
│                       │                                      │
└───────────────────────┼──────────────────────────────────────┘
                        │
                        ▼
                 ┌─────────────┐
                 │   FastAPI   │
                 │   Backend   │
                 └─────────────┘
```

### Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Google Cloud Platform                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     VPC Network                           │   │
│  │  ┌────────────────┐  ┌────────────────┐                   │   │
│  │  │  Public Subnet │  │ Private Subnet │                   │   │
│  │  │  (10.0.1.0/24) │  │  (10.0.2.0/24) │                   │   │
│  │  └───────┬────────┘  └───────┬────────┘                   │   │
│  └──────────┼───────────────────┼────────────────────────────┘   │
│             │                   │                                │
│             ▼                   ▼                                │
│  ┌──────────────────┐  ┌───────────────────┐                    │
│  │    Cloud Run     │  │   VPC Connector   │                    │
│  │   ┌──────────┐   │  │                   │                    │
│  │   │   API    │◄──┼──┤                   │                    │
│  │   │ Service  │   │  └─────────┬─────────┘                    │
│  │   └──────────┘   │            │                               │
│  │   ┌──────────┐   │            │                               │
│  │   │Migration │   │            │                               │
│  │   │   Job    │   │            │                               │
│  │   └──────────┘   │            │                               │
│  └──────────────────┘            │                               │
│                                  │                               │
│            ┌─────────────────────┼─────────────────────┐        │
│            │                     │                     │        │
│            ▼                     ▼                     ▼        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │    Cloud SQL     │  │   Memorystore    │  │   Secret     │  │
│  │   PostgreSQL     │  │     Redis        │  │   Manager    │  │
│  │   ┌──────────┐   │  │   ┌──────────┐   │  │              │  │
│  │   │ Primary  │   │  │   │  Master  │   │  │  • DB_URL    │  │
│  │   └──────────┘   │  │   └──────────┘   │  │  • REDIS_URL │  │
│  │   ┌──────────┐   │  │   ┌──────────┐   │  │  • API_KEY   │  │
│  │   │ Replica  │   │  │   │ Replica  │   │  │              │  │
│  │   │  (Prod)  │   │  │   │  (Prod)  │   │  │              │  │
│  │   └──────────┘   │  │   └──────────┘   │  │              │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Actions                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                   │
│  │    CI    │───►│  Build   │───►│  Deploy  │                   │
│  │          │    │  & Push  │    │          │                   │
│  └──────────┘    └──────────┘    └──────────┘                   │
│       │               │               │                          │
│       ▼               ▼               ▼                          │
│  • Security      • Docker        • Cloud Run                     │
│  • Lint          • Artifact      • Migrations                    │
│  • Test            Registry      • Smoke Tests                   │
│  • Docker                        • Rollback                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │  API     │     │ Database │
│          │     │          │     │          │     │          │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Upload Image   │                │                │
     │───────────────►│                │                │
     │                │ POST /extract  │                │
     │                │───────────────►│                │
     │                │                │ Create Job     │
     │                │                │───────────────►│
     │                │                │                │
     │                │  Job ID        │                │
     │                │◄───────────────│                │
     │                │                │                │
     │                │ GET /jobs/{id} │                │
     │                │───────────────►│                │
     │                │                │ Query Status   │
     │                │                │◄───────────────│
     │                │                │                │
     │                │  Progress      │                │
     │◄───────────────│◄───────────────│                │
     │                │                │                │
     │                │                │ [Complete]     │
     │                │                │                │
     │                │  Tokens        │                │
     │◄───────────────│◄───────────────│◄───────────────│
     │                │                │                │
     │ Select Token   │                │                │
     │───────────────►│                │                │
     │                │                │                │
     │ Details        │                │                │
     │◄───────────────│                │                │
     │                │                │                │
     │ Export CSS     │                │                │
     │───────────────►│                │                │
     │                │ POST /export   │                │
     │                │───────────────►│                │
     │                │                │                │
     │                │  File          │                │
     │◄───────────────│◄───────────────│                │
     │                │                │                │
```

---

## Configuration Examples

### Complete Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig(({ mode }) => ({
  root: 'frontend',

  plugins: [
    react(),
    mode === 'analyze' && visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true
    })
  ].filter(Boolean),

  build: {
    outDir: '../dist',
    sourcemap: mode !== 'production',

    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'query-vendor': ['@tanstack/react-query'],
          'state-vendor': ['zustand']
        }
      }
    },

    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: mode === 'production',
        drop_debugger: true
      }
    },

    chunkSizeWarningLimit: 500,
    cssCodeSplit: true,
    cssMinify: true
  },

  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },

  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './frontend/vitest.setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        global: {
          branches: 70,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  }
}))
```

### Complete TypeScript Configuration

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    // Type Checking
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "useUnknownInCatchVariables": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,

    // Modules
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,

    // Emit
    "noEmit": true,

    // JavaScript Support
    "allowJs": false,
    "checkJs": false,

    // Interop
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,

    // JSX
    "jsx": "react-jsx",

    // Paths
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@components/*": ["components/*"],
      "@store/*": ["store/*"],
      "@api/*": ["api/*"],
      "@types/*": ["types/*"],
      "@utils/*": ["utils/*"]
    }
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

### ESLint Configuration

```javascript
// .eslintrc.cjs
module.exports = {
  root: true,
  env: {
    browser: true,
    es2020: true,
    node: true
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    project: ['./tsconfig.json', './frontend/tsconfig.json']
  },
  plugins: [
    '@typescript-eslint',
    'react',
    'react-hooks',
    'jsx-a11y'
  ],
  rules: {
    // TypeScript
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/no-non-null-assertion': 'warn',

    // React
    'react/prop-types': 'off',
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',

    // Accessibility
    'jsx-a11y/anchor-is-valid': 'error',
    'jsx-a11y/click-events-have-key-events': 'error',
    'jsx-a11y/no-static-element-interactions': 'error'
  },
  settings: {
    react: {
      version: 'detect'
    }
  }
}
```

---

## Component Examples

### Memoized Component Pattern

```typescript
// components/TokenCard.tsx
import React, { memo, useCallback } from 'react'
import type { ColorToken } from '../types'
import './TokenCard.css'

interface TokenCardProps {
  token: ColorToken
  isSelected?: boolean
  onSelect: (id: string) => void
  onEdit: (token: ColorToken) => void
  onDelete: (id: string) => void
  onDuplicate: (id: string) => void
}

export const TokenCard = memo<TokenCardProps>(function TokenCard({
  token,
  isSelected = false,
  onSelect,
  onEdit,
  onDelete,
  onDuplicate
}) {
  // Stable callback references
  const handleSelect = useCallback(() => {
    onSelect(token.id)
  }, [onSelect, token.id])

  const handleEdit = useCallback(() => {
    onEdit(token)
  }, [onEdit, token])

  const handleDelete = useCallback(() => {
    onDelete(token.id)
  }, [onDelete, token.id])

  const handleDuplicate = useCallback(() => {
    onDuplicate(token.id)
  }, [onDuplicate, token.id])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleSelect()
    }
  }, [handleSelect])

  return (
    <div
      className={`token-card ${isSelected ? 'token-card--selected' : ''}`}
      onClick={handleSelect}
      onKeyDown={handleKeyDown}
      role="gridcell"
      tabIndex={0}
      aria-selected={isSelected}
    >
      <div className="token-card__header">
        <div
          className="token-card__swatch"
          style={{ backgroundColor: token.hex }}
          role="img"
          aria-label={`Color swatch: ${token.hex}`}
        />
        <div className="token-card__info">
          <h4 className="token-card__name">{token.name}</h4>
          <span className="token-card__hex">{token.hex}</span>
        </div>
      </div>

      <div className="token-card__metadata">
        <span className="token-card__confidence">
          {Math.round(token.confidence * 100)}% confidence
        </span>
        {token.wcagAACompliantText && (
          <span className="token-card__badge token-card__badge--success">
            WCAG AA
          </span>
        )}
      </div>

      <div className="token-card__actions">
        <button
          onClick={(e) => { e.stopPropagation(); handleEdit() }}
          aria-label={`Edit ${token.name}`}
        >
          Edit
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); handleDuplicate() }}
          aria-label={`Duplicate ${token.name}`}
        >
          Duplicate
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); handleDelete() }}
          className="token-card__action--danger"
          aria-label={`Delete ${token.name}`}
        >
          Delete
        </button>
      </div>
    </div>
  )
})
```

### Virtual List Pattern

```typescript
// components/TokenGrid.tsx
import React, { useRef, useMemo } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useTokenStore } from '../store/tokenStore'
import { useUIStore } from '../store/uiStore'
import { TokenCard } from './TokenCard'
import { matchesFilters, getSortFn } from '../utils/filters'
import './TokenGrid.css'

const CARD_HEIGHT = 200
const GRID_GAP = 16
const COLUMNS = 3

export function TokenGrid() {
  const parentRef = useRef<HTMLDivElement>(null)

  // Granular selectors
  const tokens = useTokenStore(s => s.tokens)
  const selectedTokenId = useTokenStore(s => s.selectedTokenId)
  const selectToken = useTokenStore(s => s.selectToken)
  const deleteToken = useTokenStore(s => s.deleteToken)
  const duplicateToken = useTokenStore(s => s.duplicateToken)

  const filters = useUIStore(s => s.filters)
  const sortBy = useUIStore(s => s.sortBy)

  // Memoize filtered and sorted tokens
  const filteredTokens = useMemo(() => {
    const filtered = tokens.filter(t => matchesFilters(t, filters))
    return [...filtered].sort(getSortFn(sortBy))
  }, [tokens, filters, sortBy])

  // Calculate rows for virtualization
  const rowCount = Math.ceil(filteredTokens.length / COLUMNS)

  const virtualizer = useVirtualizer({
    count: rowCount,
    getScrollElement: () => parentRef.current,
    estimateSize: () => CARD_HEIGHT + GRID_GAP,
    overscan: 2
  })

  const handleEdit = useCallback((token: ColorToken) => {
    // Open edit modal
  }, [])

  if (filteredTokens.length === 0) {
    return (
      <div className="token-grid__empty" role="status">
        <p>No tokens match your filters</p>
      </div>
    )
  }

  return (
    <div
      ref={parentRef}
      className="token-grid__container"
      style={{ height: '100%', overflow: 'auto' }}
    >
      <div
        className="token-grid"
        role="grid"
        aria-label="Color tokens"
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: 'relative'
        }}
      >
        {virtualizer.getVirtualItems().map(virtualRow => {
          const rowIndex = virtualRow.index
          const startIndex = rowIndex * COLUMNS

          return (
            <div
              key={virtualRow.key}
              className="token-grid__row"
              role="row"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`
              }}
            >
              {Array.from({ length: COLUMNS }).map((_, colIndex) => {
                const tokenIndex = startIndex + colIndex
                const token = filteredTokens[tokenIndex]

                if (!token) return null

                return (
                  <TokenCard
                    key={token.id}
                    token={token}
                    isSelected={token.id === selectedTokenId}
                    onSelect={selectToken}
                    onEdit={handleEdit}
                    onDelete={deleteToken}
                    onDuplicate={duplicateToken}
                  />
                )
              })}
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

### Custom Hook Pattern

```typescript
// hooks/useColorToken.ts
import { useMemo } from 'react'
import { useTokenStore } from '../store/tokenStore'

export function useSelectedToken() {
  const tokens = useTokenStore(s => s.tokens)
  const selectedId = useTokenStore(s => s.selectedTokenId)

  return useMemo(
    () => tokens.find(t => t.id === selectedId) ?? null,
    [tokens, selectedId]
  )
}

export function useTokensByType(type: string) {
  const tokens = useTokenStore(s => s.tokens)

  return useMemo(
    () => tokens.filter(t => t.type === type),
    [tokens, type]
  )
}

export function useColorContrast(foreground: string, background: string) {
  return useMemo(() => {
    const getLuminance = (hex: string) => {
      const rgb = parseInt(hex.slice(1), 16)
      const r = (rgb >> 16) & 0xff
      const g = (rgb >> 8) & 0xff
      const b = (rgb >> 0) & 0xff

      const [rs, gs, bs] = [r, g, b].map(c => {
        c = c / 255
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
      })

      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
    }

    const l1 = getLuminance(foreground)
    const l2 = getLuminance(background)
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)

    return {
      ratio,
      passesAA: ratio >= 4.5,
      passesAAA: ratio >= 7,
      passesAALarge: ratio >= 3
    }
  }, [foreground, background])
}
```

---

## Terraform Examples

### Complete Cloud Run Module

```hcl
# deploy/terraform/modules/cloudrun/main.tf

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "image" {
  type = string
}

variable "vpc_connector" {
  type = string
}

variable "service_account" {
  type = string
}

variable "secrets" {
  type = map(string)
}

locals {
  is_production = var.environment == "production"

  cpu_limit    = local.is_production ? "2" : "1"
  memory_limit = local.is_production ? "1Gi" : "512Mi"
  min_scale    = local.is_production ? 1 : 0
  max_scale    = local.is_production ? 100 : 10
  concurrency  = 80
}

resource "google_cloud_run_v2_service" "main" {
  name     = "${var.project_id}-api-${var.environment}"
  location = var.region

  template {
    containers {
      image = var.image

      resources {
        limits = {
          cpu    = local.cpu_limit
          memory = local.memory_limit
        }
        cpu_idle          = !local.is_production
        startup_cpu_boost = true
      }

      # Environment variables
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "LOG_LEVEL"
        value = local.is_production ? "INFO" : "DEBUG"
      }

      # Secrets from Secret Manager
      dynamic "env" {
        for_each = var.secrets
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value
              version = "latest"
            }
          }
        }
      }

      # Startup probe
      startup_probe {
        initial_delay_seconds = 0
        timeout_seconds       = 10
        period_seconds        = 3
        failure_threshold     = 10

        http_get {
          path = "/health"
          port = 8000
        }
      }

      # Liveness probe
      liveness_probe {
        timeout_seconds   = 5
        period_seconds    = 15
        failure_threshold = 3

        http_get {
          path = "/health"
          port = 8000
        }
      }

      ports {
        container_port = 8000
      }
    }

    # Scaling
    scaling {
      min_instance_count = local.min_scale
      max_instance_count = local.max_scale
    }

    # Concurrency
    max_instance_request_concurrency = local.concurrency

    # Timeout
    timeout = "300s"

    # VPC access
    vpc_access {
      connector = var.vpc_connector
      egress    = "PRIVATE_RANGES_ONLY"
    }

    # Service account
    service_account = var.service_account
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image
    ]
  }
}

# IAM for public access (if needed)
resource "google_cloud_run_service_iam_member" "public" {
  count = var.environment == "production" ? 1 : 0

  location = google_cloud_run_v2_service.main.location
  service  = google_cloud_run_v2_service.main.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "url" {
  value = google_cloud_run_v2_service.main.uri
}

output "name" {
  value = google_cloud_run_v2_service.main.name
}
```

### Complete Monitoring Module

```hcl
# deploy/terraform/modules/monitoring/main.tf

variable "project_id" {
  type = string
}

variable "environment" {
  type = string
}

variable "service_name" {
  type = string
}

variable "notification_email" {
  type = string
}

# Email notification channel
resource "google_monitoring_notification_channel" "email" {
  display_name = "${var.environment} Email Alerts"
  type         = "email"

  labels = {
    email_address = var.notification_email
  }
}

# Error rate alert
resource "google_monitoring_alert_policy" "error_rate" {
  display_name = "[${var.environment}] High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "5xx Error Rate > 5%"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        AND resource.labels.service_name = "${var.service_name}"
        AND metric.type = "run.googleapis.com/request_count"
        AND metric.labels.response_code_class = "5xx"
      EOT

      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email.id
  ]

  alert_strategy {
    auto_close = "604800s"
  }

  documentation {
    content   = "Error rate exceeded 5% for service ${var.service_name}"
    mime_type = "text/markdown"
  }
}

# Latency alert
resource "google_monitoring_alert_policy" "latency" {
  display_name = "[${var.environment}] High Latency"
  combiner     = "OR"

  conditions {
    display_name = "P95 Latency > 2s"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        AND resource.labels.service_name = "${var.service_name}"
        AND metric.type = "run.googleapis.com/request_latencies"
      EOT

      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 2000

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_95"
        cross_series_reducer = "REDUCE_MEAN"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email.id
  ]
}

# Instance count alert
resource "google_monitoring_alert_policy" "scaling" {
  display_name = "[${var.environment}] Max Instances Reached"
  combiner     = "OR"

  conditions {
    display_name = "Instance count at max"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        AND resource.labels.service_name = "${var.service_name}"
        AND metric.type = "run.googleapis.com/container/instance_count"
      EOT

      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 90  # Adjust based on max_instances

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.email.id
  ]
}
```

---

## CI/CD Examples

### Complete CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Install security tools
        run: pip install pip-audit bandit safety

      - name: pip-audit
        run: pip-audit --require-hashes --strict

      - name: Bandit
        run: |
          bandit -r app -f json -o bandit.json --severity-level high
          if jq -e '.results | length > 0' bandit.json; then
            echo "::error::Security vulnerabilities found"
            jq '.results' bandit.json
            exit 1
          fi

      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  lint:
    name: Lint
    runs-on: ubuntu-latest
    strategy:
      matrix:
        tool: [ruff, mypy]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Run ${{ matrix.tool }}
        run: |
          pip install ${{ matrix.tool }}
          if [ "${{ matrix.tool }}" = "ruff" ]; then
            ruff check app --output-format=github
          else
            mypy app --strict
          fi

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Install dependencies
        run: pip install -e ".[test]"

      - name: Run migrations
        run: alembic upgrade head
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test

      - name: Run tests
        run: pytest tests -v --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
          fail_ci_if_error: true

  frontend:
    name: Frontend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Type check
        run: npm run type-check

      - name: Lint
        run: npm run lint

      - name: Test
        run: npm run test:coverage

      - name: Build
        run: npm run build

  docker:
    name: Docker
    runs-on: ubuntu-latest
    needs: [security, test, frontend]
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - name: Build
        uses: docker/build-push-action@v5
        with:
          context: .
          target: production
          push: false
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ github.sha }}
          exit-code: 1
          severity: CRITICAL,HIGH
```

---

## File Inventory

### Frontend Files

| Path | Type | Lines | Description |
|------|------|-------|-------------|
| `src/App.tsx` | Component | ~100 | Main application |
| `src/main.tsx` | Entry | ~20 | React entry point |
| `src/components/*.tsx` | Component | ~4,070 | 22 components |
| `src/store/tokenStore.ts` | State | ~200 | Zustand store |
| `src/api/hooks.ts` | Hooks | ~150 | TanStack Query |
| `src/api/client.ts` | API | ~50 | Fetch client |
| `src/types/index.ts` | Types | ~200 | TypeScript types |
| `src/config/tokenTypeRegistry.tsx` | Config | ~300 | Token schemas |

### Infrastructure Files

| Path | Type | Lines | Description |
|------|------|-------|-------------|
| `Dockerfile` | Docker | ~80 | Multi-stage build |
| `Dockerfile.cloudrun` | Docker | ~40 | Cloud Run image |
| `docker-compose.yml` | Docker | ~150 | Local dev |
| `deploy/terraform/*.tf` | Terraform | ~1,500 | IaC |
| `.github/workflows/*.yml` | CI/CD | ~600 | GitHub Actions |
| `deploy/scripts/*.sh` | Scripts | ~300 | Deploy scripts |

---

## Glossary

| Term | Definition |
|------|------------|
| **Code Splitting** | Technique to split JS bundle into smaller chunks |
| **Cold Start** | Delay when Cloud Run starts new instance |
| **HA** | High Availability - redundancy for failover |
| **IAC** | Infrastructure as Code |
| **Memoization** | Caching function results to avoid recomputation |
| **OIDC** | OpenID Connect - authentication protocol |
| **PITR** | Point-in-Time Recovery for databases |
| **Tree-shaking** | Dead code elimination in bundles |
| **VPC Connector** | Bridge between Cloud Run and VPC |
| **Virtualization** | Rendering only visible list items |
| **WCAG** | Web Content Accessibility Guidelines |
| **Workload Identity** | GCP identity federation for CI/CD |

---

## References

### Documentation

- [React 18 Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Vite Guide](https://vitejs.dev/guide)
- [Zustand Documentation](https://zustand-demo.pmnd.rs)
- [TanStack Query](https://tanstack.com/query)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [GitHub Actions](https://docs.github.com/en/actions)

### Standards

- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref)
- [W3C Design Tokens](https://design-tokens.github.io/community-group)

---

*This appendix provides technical reference material for implementing the recommendations in this analysis.*
