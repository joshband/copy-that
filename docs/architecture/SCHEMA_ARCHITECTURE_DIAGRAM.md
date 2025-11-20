# Schema Architecture Diagrams

**Date:** 2025-11-18
**Version:** 2.0 (Revised Architecture with Adapters)

---

## 📚 Related Documentation

- **[ROADMAP.md](../../ROADMAP.md)** - Phase 4 overview in project roadmap
- **[Phase 4 Revised Implementation Plan](../planning/PHASE_4_REVISED_IMPLEMENTATION_PLAN.md)** - Detailed week-by-week guide
- **[Original Schema Solution](../analysis/STRUCTURED_OUTPUTS_SCHEMA_SOLUTION.md)** - Original analysis

---

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "Image Input"
        IMG[UI Screenshot/Image]
    end

    subgraph "Extraction Layer"
        E1[Color Extractor]
        E2[Spacing Extractor]
        E3[Shadow Extractor]
        E4[Typography Extractor]
        E5[AI Extractor<br/>Claude Structured Outputs]

        IMG --> E1
        IMG --> E2
        IMG --> E3
        IMG --> E4
        IMG --> E5
    end

    subgraph "Schema Layers"
        subgraph "Core Schema Layer"
            CORE[Core Token Schema<br/>token-core-v1.json<br/><br/>Minimal shared definitions:<br/>- hex, confidence, type]
        end

        subgraph "API Schema Layer"
            API[API Token Schema<br/>token-api-v1.json<br/><br/>Public contract:<br/>+ semantic_name<br/>+ design_intent<br/>+ extractors]
        end

        subgraph "Frontend Schema"
            FE[Frontend Schema<br/><br/>UI metadata:<br/>+ displayName<br/>+ confidenceBadge<br/>+ confidenceClass]
        end

        subgraph "Generator Schema"
            GEN[Generator Schema<br/><br/>Code generation:<br/>+ css_var_name<br/>+ usage_context]
        end

        subgraph "Database Schema"
            DB[Database Tables<br/><br/>Structured persistence:<br/>+ id, foreign keys<br/>+ indexes<br/>+ audit fields]
        end
    end

    subgraph "Adapter Layer"
        A1[Extractor Adapter<br/>Internal → API]
        A2[Frontend Adapter<br/>API → UI Model]
        A3[Generator Adapter<br/>API → Generator Model]
        A4[Database Adapter<br/>API → DB Model]
    end

    subgraph "Consumer Layer"
        C1[React Frontend<br/>TypeScript + Zod]
        C2[Code Generators<br/>CSS/SCSS/JS/JSON]
        C3[PostgreSQL Database<br/>Structured Tables]
    end

    %% Extraction to Core
    E1 --> CORE
    E2 --> CORE
    E3 --> CORE
    E4 --> CORE
    E5 -.->|Structured Outputs| CORE

    %% Core to API via Adapter
    CORE --> A1
    A1 --> API

    %% API to Consumers via Adapters
    API --> A2
    API --> A3
    API --> A4

    A2 --> FE
    A3 --> GEN
    A4 --> DB

    %% Final Consumers
    FE --> C1
    GEN --> C2
    DB --> C3

    %% Styling
    classDef coreStyle fill:#90EE90,stroke:#2E7D32,stroke-width:2px
    classDef apiStyle fill:#87CEEB,stroke:#1976D2,stroke-width:2px
    classDef adapterStyle fill:#FFD700,stroke:#F57C00,stroke-width:2px
    classDef consumerStyle fill:#DDA0DD,stroke:#7B1FA2,stroke-width:2px
    classDef extractorStyle fill:#FFB6C1,stroke:#C2185B,stroke-width:2px

    class CORE coreStyle
    class API apiStyle
    class A1,A2,A3,A4 adapterStyle
    class FE,GEN,DB consumerStyle
    class E1,E2,E3,E4,E5 extractorStyle
```

---

## 2. Schema Layering & Dependencies

```mermaid
graph LR
    subgraph "Schema Hierarchy"
        CORE[Core Schema<br/>Minimal Shared]

        CORE --> API[API Schema<br/>+ Metadata]
        CORE --> INT[Internal Schema<br/>+ Provenance]

        API --> FE[Frontend Schema<br/>+ UI Helpers]
        API --> GEN[Generator Schema<br/>+ Code Gen]
        API --> DB[Database Schema<br/>+ Persistence]
    end

    style CORE fill:#90EE90,stroke:#2E7D32,stroke-width:3px
    style API fill:#87CEEB,stroke:#1976D2,stroke-width:2px
    style INT fill:#FFA07A,stroke:#D84315,stroke-width:2px
    style FE fill:#DDA0DD,stroke:#7B1FA2,stroke-width:2px
    style GEN fill:#F0E68C,stroke:#F57C00,stroke-width:2px
    style DB fill:#ADD8E6,stroke:#0277BD,stroke-width:2px
```

---

## 3. Data Flow with Adapters (Detailed)

```mermaid
sequenceDiagram
    participant IMG as UI Screenshot
    participant EXT as AI Extractor
    participant SO as Claude Structured<br/>Outputs
    participant CORE as Core Schema
    participant ADP1 as Extractor<br/>Adapter
    participant API as API Schema
    participant ADP2 as Frontend<br/>Adapter
    participant FE as Frontend UI
    participant ADP3 as DB Adapter
    participant DB as Database

    IMG->>EXT: Upload image
    EXT->>SO: Extract tokens with<br/>Structured Outputs
    SO-->>EXT: Guaranteed valid<br/>Core Schema
    EXT->>CORE: Core Token<br/>(hex, confidence)

    Note over CORE,ADP1: Translation Layer

    CORE->>ADP1: Transform
    ADP1->>ADP1: Add metadata:<br/>- semantic_name<br/>- design_intent<br/>- extractors
    ADP1->>API: API Token<br/>(core + metadata)

    par Frontend Path
        API->>ADP2: Transform
        ADP2->>ADP2: Add UI helpers:<br/>- displayName<br/>- confidenceBadge
        ADP2->>FE: UI Token
        FE->>FE: Render with<br/>confidence badges
    and Database Path
        API->>ADP3: Transform
        ADP3->>ADP3: Map to DB model:<br/>- foreign keys<br/>- audit fields
        ADP3->>DB: Insert structured<br/>row (not JSONB)
        DB-->>ADP3: Row ID
    end
```

---

## 4. Adapter Pattern Architecture

```mermaid
classDiagram
    class TokenAdapter~TInternal, TAPI~ {
        <<Protocol>>
        +to_api(internal: TInternal) TAPI
        +from_api(api: TAPI) TInternal
    }

    class ColorTokenAdapter {
        +to_api(CoreColorToken) APIColorToken
        +from_api(APIColorToken) CoreColorToken
        -_generate_semantic_name(hex) string
        -_compute_design_intent() string
    }

    class FrontendAdapter {
        +toUIModel(APIColorToken) UIColorToken
        +toAPIModel(UIColorToken) APIColorToken
        -getConfidenceBadge(confidence) string
        -getConfidenceClass(confidence) string
    }

    class GeneratorAdapter {
        +toGeneratorModel(APIColorToken) GeneratorToken
        -toCSSVarName(name) string
        -computeUsageContext() string
    }

    class DatabaseAdapter {
        +toDBModel(APIColorToken) ColorTokenDB
        +fromDBModel(ColorTokenDB) APIColorToken
        -mapRelationships() void
    }

    TokenAdapter <|.. ColorTokenAdapter : implements
    TokenAdapter <|.. FrontendAdapter : implements
    TokenAdapter <|.. GeneratorAdapter : implements
    TokenAdapter <|.. DatabaseAdapter : implements

    class CoreColorToken {
        +hex: string
        +confidence: float
        +token_type: string
    }

    class APIColorToken {
        +hex: string
        +confidence: float
        +token_type: string
        +semantic_name: string
        +design_intent: string
        +extractors: List~string~
        +variant_type: string
        +created_at: datetime
    }

    class UIColorToken {
        +APIColorToken fields
        +displayName: string
        +confidenceBadge: string
        +confidenceClass: string
    }

    class GeneratorToken {
        +hex: string
        +css_var_name: string
        +confidence: float
        +semantic_name: string
    }

    class ColorTokenDB {
        +id: int
        +extraction_job_id: int
        +hex: string
        +confidence: float
        +semantic_name: string
        +created_at: datetime
    }

    ColorTokenAdapter --> CoreColorToken : reads
    ColorTokenAdapter --> APIColorToken : produces
    FrontendAdapter --> APIColorToken : reads
    FrontendAdapter --> UIColorToken : produces
    GeneratorAdapter --> APIColorToken : reads
    GeneratorAdapter --> GeneratorToken : produces
    DatabaseAdapter --> APIColorToken : reads
    DatabaseAdapter --> ColorTokenDB : produces
```

---

## 5. Before vs After Architecture

### Before (Tight Coupling)

```mermaid
graph LR
    subgraph "Original Architecture - TIGHT COUPLING"
        EXT[Extractors]
        BE[Backend]
        FE[Frontend]
        GEN[Generators]
        DB[(Database<br/>JSONB)]

        SCHEMA[SINGLE UNIFIED SCHEMA<br/>token-schema-v1.json]

        EXT -->|depends on| SCHEMA
        BE -->|depends on| SCHEMA
        FE -->|depends on| SCHEMA
        GEN -->|depends on| SCHEMA
        DB -->|depends on| SCHEMA

        SCHEMA -.->|any change breaks<br/>ALL systems| EXT
        SCHEMA -.->|coordinated<br/>deployments| BE
        SCHEMA -.->|no independent<br/>evolution| FE
    end

    style SCHEMA fill:#FF6B6B,stroke:#C92A2A,stroke-width:3px,color:#FFF
    style EXT fill:#FFB3B3
    style BE fill:#FFB3B3
    style FE fill:#FFB3B3
    style GEN fill:#FFB3B3
    style DB fill:#FFB3B3
```

### After (Loose Coupling)

```mermaid
graph TB
    subgraph "Revised Architecture - LOOSE COUPLING"
        subgraph "Core"
            CORE[Core Schema<br/>token-core-v1.json<br/><br/>Minimal shared]
        end

        subgraph "Adapters"
            A1[Extractor<br/>Adapter]
            A2[Frontend<br/>Adapter]
            A3[Generator<br/>Adapter]
            A4[Database<br/>Adapter]
        end

        subgraph "Context-Specific Schemas"
            API[API Schema<br/>token-api-v1.json]
            FE[Frontend Schema<br/>+ UI helpers]
            GEN[Generator Schema<br/>+ code gen]
            DB[Database Schema<br/>+ structured tables]
        end

        subgraph "Consumers"
            EXT[Extractors]
            FE_APP[Frontend App]
            GEN_APP[Generators]
            DB_APP[(PostgreSQL)]
        end

        CORE --> A1
        A1 --> API

        API --> A2
        API --> A3
        API --> A4

        A2 --> FE
        A3 --> GEN
        A4 --> DB

        EXT --> CORE
        FE --> FE_APP
        GEN --> GEN_APP
        DB --> DB_APP
    end

    style CORE fill:#90EE90,stroke:#2E7D32,stroke-width:3px
    style A1 fill:#FFD700,stroke:#F57C00
    style A2 fill:#FFD700,stroke:#F57C00
    style A3 fill:#FFD700,stroke:#F57C00
    style A4 fill:#FFD700,stroke:#F57C00
    style API fill:#87CEEB,stroke:#1976D2
    style FE fill:#DDA0DD,stroke:#7B1FA2
    style GEN fill:#F0E68C,stroke:#F57C00
    style DB fill:#ADD8E6,stroke:#0277BD
```

---

## 6. Claude Structured Outputs Integration

```mermaid
graph TB
    subgraph "AI Extraction with Structured Outputs"
        IMG[UI Screenshot]

        subgraph "Claude API"
            PROMPT[Extraction Prompt<br/>'Extract design tokens']
            SCHEMA_DEF[JSON Schema Definition<br/>CoreColorToken.model_json_schema]
            SO[Claude Structured Outputs<br/>response_format]
            LLM[Claude Sonnet 4.5]
        end

        subgraph "Validation"
            VALID{Schema<br/>Valid?}
            OUTPUT[Guaranteed Valid<br/>Core Token]
        end

        IMG --> PROMPT
        SCHEMA_DEF --> SO
        PROMPT --> SO
        SO --> LLM
        LLM --> VALID
        VALID -->|✅ Always| OUTPUT

        OUTPUT --> CORE[Core Schema]
        CORE --> ADAPTER[Adapter Layer]
        ADAPTER --> API[API Schema]
    end

    style SO fill:#90EE90,stroke:#2E7D32,stroke-width:3px
    style OUTPUT fill:#90EE90,stroke:#2E7D32,stroke-width:2px
    style VALID fill:#4CAF50,stroke:#2E7D32,stroke-width:2px
```

---

## 7. Database Schema (Structured Tables)

```mermaid
erDiagram
    EXTRACTION_JOBS ||--o{ COLOR_TOKENS : contains
    EXTRACTION_JOBS ||--o{ SPACING_TOKENS : contains
    EXTRACTION_JOBS ||--o{ SHADOW_TOKENS : contains
    EXTRACTION_JOBS ||--o{ EXTRACTION_JOBS : "parent variant"

    EXTRACTION_JOBS {
        int id PK
        text url
        string status
        string variant_type
        int parent_job_id FK
        timestamp created_at
        timestamp completed_at
    }

    COLOR_TOKENS {
        int id PK
        int extraction_job_id FK
        string hex "CHECK hex ~ '^#[0-9A-Fa-f]{6}$'"
        float confidence "CHECK 0 <= confidence <= 1"
        string token_type
        string semantic_name "INDEX"
        text design_intent
        string variant_type "INDEX"
        array extractors
        jsonb algorithm_metadata
        timestamp created_at
    }

    SPACING_TOKENS {
        int id PK
        int extraction_job_id FK
        float value "CHECK value >= 0"
        string unit
        float confidence "CHECK 0 <= confidence <= 1"
        string semantic_name
        string variant_type "INDEX"
        timestamp created_at
    }

    SHADOW_TOKENS {
        int id PK
        int extraction_job_id FK
        text css_value
        int elevation_level "CHECK 1 <= elevation <= 5"
        float confidence
        string semantic_name
        string variant_type "INDEX"
        timestamp created_at
    }
```

---

## 8. API Versioning Strategy

```mermaid
graph TB
    subgraph "Client Requests"
        C1[Frontend Client<br/>Accept-Version: v2]
        C2[Legacy Client<br/>Accept-Version: v1]
        C3[Generator<br/>No header - default v1]
    end

    subgraph "API Gateway"
        GATEWAY[FastAPI Gateway<br/>Version Negotiation]

        subgraph "Version Routes"
            V1[/api/v1/extract]
            V2[/api/v2/extract]
        end

        subgraph "Adapters"
            AV1[V1 Adapter<br/>Strips metadata]
            AV2[V2 Adapter<br/>Full metadata]
        end
    end

    subgraph "Internal Services"
        EXTRACTOR[Token Extractor<br/>Always produces v2]
    end

    C1 -->|Accept-Version: v2| GATEWAY
    C2 -->|Accept-Version: v1| GATEWAY
    C3 -->|default| GATEWAY

    GATEWAY --> V1
    GATEWAY --> V2

    V1 --> AV1
    V2 --> AV2

    AV1 --> EXTRACTOR
    AV2 --> EXTRACTOR

    AV1 -.->|strip metadata| C2
    AV2 -.->|full tokens| C1
    V1 -.->|legacy format| C3

    style V2 fill:#90EE90,stroke:#2E7D32,stroke-width:2px
    style AV2 fill:#90EE90,stroke:#2E7D32
    style V1 fill:#FFE5B4,stroke:#F57C00
    style AV1 fill:#FFE5B4,stroke:#F57C00
```

---

## 9. Schema Registry & Versioning

```mermaid
graph TB
    subgraph "Development"
        DEV[Developer<br/>Updates Schema]
    end

    subgraph "Buf Schema Registry"
        REGISTRY[Schema Registry<br/>buf.build/copythis]

        subgraph "Schema Versions"
            V1[token-core-v1.0.0]
            V2[token-core-v1.1.0<br/>+ optional fields]
            V3[token-core-v2.0.0<br/>BREAKING]
        end

        BREAKING{Breaking<br/>Change<br/>Detector}
    end

    subgraph "Consumers"
        BE[Backend<br/>Uses v1.1.0]
        FE[Frontend<br/>Uses v1.0.0]
        GEN[Generators<br/>Uses v1.1.0]
    end

    DEV -->|buf push| REGISTRY
    REGISTRY --> BREAKING
    BREAKING -->|✅ Compatible| V2
    BREAKING -->|❌ Breaking| V3

    V1 --> BE
    V1 --> FE
    V2 --> GEN

    V3 -.->|Migration required| BE
    V3 -.->|Migration required| FE

    style BREAKING fill:#FFD700,stroke:#F57C00,stroke-width:2px
    style V3 fill:#FF6B6B,stroke:#C92A2A,stroke-width:2px
    style V2 fill:#90EE90,stroke:#2E7D32
    style V1 fill:#87CEEB,stroke:#1976D2
```

---

## 10. Error Handling & Graceful Degradation

```mermaid
graph TB
    subgraph "API Response"
        RESPONSE[API Token Response]
    end

    subgraph "Frontend Validation"
        ZOD[Zod Schema Validator]
        SAFE{safeParse<br/>Valid?}
    end

    subgraph "Error Handling"
        PARTIAL[Partial Parser<br/>Use what we can]
        FALLBACK[Fallback to<br/>Hex-only display]
        LOG[Log validation<br/>errors to Sentry]
    end

    subgraph "UI Rendering"
        FULL[Full UI<br/>+ confidence + semantic name]
        BASIC[Basic UI<br/>hex only]
    end

    RESPONSE --> ZOD
    ZOD --> SAFE

    SAFE -->|✅ Valid| FULL
    SAFE -->|❌ Invalid| PARTIAL

    PARTIAL -->|Some fields OK| BASIC
    PARTIAL -->|All fields bad| FALLBACK

    PARTIAL --> LOG
    FALLBACK --> LOG

    style SAFE fill:#4CAF50,stroke:#2E7D32,stroke-width:2px
    style PARTIAL fill:#FFD700,stroke:#F57C00,stroke-width:2px
    style FALLBACK fill:#FF9800,stroke:#E65100,stroke-width:2px
    style LOG fill:#F44336,stroke:#B71C1C
```

---

## Key Architecture Principles

### 1. Loose Coupling
- ✅ Each system has its own schema
- ✅ Adapters translate between schemas
- ✅ Systems evolve independently

### 2. Graceful Degradation
- ✅ `safeParse()` instead of `parse()`
- ✅ Partial parsing for recoverable errors
- ✅ Fallback UI for missing data

### 3. Type Safety
- ✅ Pydantic (Python backend)
- ✅ TypeScript (Frontend)
- ✅ Zod (Runtime validation)
- ✅ Claude Structured Outputs (AI)

### 4. Structured Data
- ✅ Relational tables (not JSONB)
- ✅ Foreign keys + indexes
- ✅ Queryable metadata

### 5. Schema Versioning
- ✅ Buf Schema Registry
- ✅ Semantic versioning
- ✅ Breaking change detection
- ✅ API version negotiation

---

## Legend

```mermaid
graph LR
    CORE[Core Schema Layer]
    API[API Schema Layer]
    ADAPTER[Adapter Layer]
    CONSUMER[Consumer Layer]
    EXTRACTOR[Extractor Layer]

    style CORE fill:#90EE90,stroke:#2E7D32,stroke-width:2px
    style API fill:#87CEEB,stroke:#1976D2,stroke-width:2px
    style ADAPTER fill:#FFD700,stroke:#F57C00,stroke-width:2px
    style CONSUMER fill:#DDA0DD,stroke:#7B1FA2,stroke-width:2px
    style EXTRACTOR fill:#FFB6C1,stroke:#C2185B,stroke-width:2px
```

- 🟢 **Green (Core):** Minimal shared schema
- 🔵 **Blue (API):** Public API contract
- 🟡 **Yellow (Adapter):** Translation layer
- 🟣 **Purple (Consumer):** Final consumers
- 🔴 **Pink (Extractor):** Token extractors

---

**Document Version:** 2.0
**Last Updated:** 2025-11-18
**Related:** [Phase 4 Revised Implementation Plan](../planning/PHASE_4_REVISED_IMPLEMENTATION_PLAN.md)
