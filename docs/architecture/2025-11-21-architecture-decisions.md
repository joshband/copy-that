# Architecture Decision Records (ADRs)

**Version:** 1.0.0
**Last Updated:** 2025-11-20

---

## Summary of Decisions

| ID | Title | Status | Date | Key Rationale |
|----|-------|--------|------|---------------|
| ADR-001 | FastAPI + Python | ACCEPTED | 2025-11-15 | AI/ML ecosystem, async, type-safe |
| ADR-002 | Adapter Pattern | ACCEPTED | 2025-11-15 | Decouple Core/API/Database, independent evolution |
| ADR-003 | Claude Sonnet 4.5 | ACCEPTED | 2025-11-15 | 95% accuracy, $0.015/extraction, Structured Outputs |
| ADR-004 | React + Vite | ACCEPTED | 2025-11-15 | Fast iteration, large ecosystem, educational focus |
| ADR-005 | Pydantic v2 | ACCEPTED | 2025-11-15 | 5-10x faster, auto-schema, FastAPI integration |
| ADR-006 | Neon PostgreSQL | ACCEPTED | 2025-11-15 | Branching, serverless, cost-effective |
| ADR-007 | Zustand | ACCEPTED | 2025-11-20 | 3KB bundle, minimal boilerplate, type-safe |
| ADR-008 | Domain-Driven Design | ACCEPTED | 2025-11-15 | Clear boundaries, testable, scalable |
| ADR-009 | Hybrid TDD | ACCEPTED | 2025-11-20 | TDD for core, Code-First for UI |
| ADR-010 | W3C Design Tokens | ACCEPTED | 2025-11-15 | Industry standard, token references, extensible |

---

## ADR-001: FastAPI + Python Backend

**Status:** ACCEPTED

**Decision:** Use FastAPI with Python 3.11+ for backend

**Rationale:**
- Python AI/ML ecosystem (Claude SDK, OpenCV, librosa, NetworkX)
- Async performance (20K+ req/sec)
- Type-safe with Pydantic v2
- Automatic OpenAPI docs

**Tradeoffs:**
- Python vs Node.js: Win on AI/ML, lose on deployment
- FastAPI vs Django: Win on async, lose on batteries-included

**Alternatives Rejected:**
- Node.js (weaker AI/ML libraries)
- Go (weak ecosystem)
- Ruby (slower, declining popularity)

---

## ADR-002: Adapter Pattern for Schema Transformation

**Status:** ACCEPTED

**Decision:** Three-layer pattern: Core Schema → Adapter → API Schema

**Rationale:**
- Decouple internal logic from API contract
- Independent evolution (API changes don't break core)
- Testable (Core is pure)
- Flexible (add new output formats later)

**Pattern:**
```
Core Schema (Pydantic)
    ↓ (Adapter)
API Schema (Pydantic)
    ↓ (HTTP)
Frontend Zod Schema
```

**Tradeoffs:**
- More code but better separation of concerns

---

## ADR-003: Claude Sonnet 4.5 with Structured Outputs

**Status:** ACCEPTED

**Decision:** Use Claude Sonnet 4.5 for all AI extraction

**Rationale:**
- Structured Outputs guarantee schema compliance
- $0.015 per extraction (50% cheaper than GPT-4 Vision)
- 95% accuracy on color extraction
- <3 seconds per image

**Cost Model:**
- Per-image: $0.015 (1K input, 500 output tokens)
- Batch 25 images: $0.375

**Alternatives Rejected:**
- GPT-4 Vision (2x cost, no Structured Outputs)
- Open source models (70-80% accuracy, infrastructure overhead)

---

## ADR-004: React + Vite for Frontend

**Status:** ACCEPTED

**Decision:** React 18 + Vite 5, defer Next.js to Phase 7+ if needed

**Rationale:**
- Fast iteration (Vite HMR <1 second)
- Large ecosystem (react-force-graph, Recharts)
- Easy educational components
- Migration path to Next.js later

**Tradeoffs:**
- No SSR/SEO (acceptable for MVP)
- Manual routing (React Router)

**Alternatives Rejected:**
- Next.js (overengineering for MVP, can migrate later)
- Vue (smaller ecosystem)
- Svelte (smallest ecosystem)

---

## ADR-005: Pydantic v2 for Schema Validation

**Status:** ACCEPTED

**Decision:** Use Pydantic v2 for all Python validation

**Rationale:**
- 5-10x faster (Rust core)
- Native type hints
- Auto JSON schema generation
- FastAPI integration (zero boilerplate)

**Tradeoffs:**
- Migration from v1 (worth it for performance)

---

## ADR-006: Neon PostgreSQL Database

**Status:** ACCEPTED

**Decision:** Neon PostgreSQL for primary database

**Rationale:**
- Branching (test migrations safely)
- Serverless auto-scaling (pay-per-use)
- Full PostgreSQL features (JSONB, joins)
- Cost-effective (free tier for MVP)

**Tradeoffs:**
- No Realtime (can add WebSocket layer)
- Manual operations (no GUI admin)

---

## ADR-007: Zustand for State Management

**Status:** ACCEPTED

**Decision:** Zustand for frontend state management

**Rationale:**
- 3KB bundle (vs 12KB Redux)
- Minimal boilerplate (no actions/reducers)
- Type-safe (TypeScript inference)
- No Provider wrapping

**Tradeoffs:**
- Smaller community (vs Redux)
- Less mature tooling

---

## ADR-008: Domain-Driven Design Architecture

**Status:** ACCEPTED

**Decision:** DDD four-layer architecture

**Rationale:**
- Clear separation (application, domain, infrastructure, interfaces)
- Testable (domain is pure)
- Scalable (ready for microservices)
- Maintainable (easy to understand)

**Layers:**
```
Interfaces (API, CLI, WebSocket)
    ↓
Application (Use cases, orchestrators)
    ↓
Domain (Business logic, entities)
    ↓
Infrastructure (Database, APIs, storage)
```

---

## ADR-009: Hybrid TDD Approach

**Status:** ACCEPTED

**Decision:** TDD for core logic, Code-First for UI components

**Rationale:**
- Core extractors need reliability (AI integration is expensive to debug)
- UI components need speed (educational components benefit from iteration)
- Refactor UI to TDD in Phase 5

**Coverage:**
- Core: 100% TDD (extractors, adapters, orchestrators, APIs)
- UI: Code-First initially, TDD in Phase 5

---

## ADR-010: W3C Design Token Format

**Status:** ACCEPTED

**Decision:** W3C Design Tokens as base schema

**Rationale:**
- Industry standard (interoperable)
- Token references (`{color.primary}`)
- Extensible (`$extensions`)
- Future-proof

**Extensions:**
- Confidence scores
- Extraction metadata
- Custom properties

---

## Key Technical Decisions

### Schema Pipeline
- JSON Schema (source of truth)
- ↓ (code generation)
- Pydantic (backend)
- Zod (frontend)

### Token References
- Syntax: `{color.primary}`, `{spacing.md}`
- Resolver: NetworkX graph traversal
- Circular reference detection

### Error Handling
- Custom exceptions (ExtractionError, InvalidImageError)
- Graceful degradation (safeParse on frontend)
- Structured logging (Sentry)

### Performance Optimization
- Frontend code splitting (lazy load visualizers)
- Backend async processing (parallel extraction)
- Database indexes (covering indexes)
- Prompt caching (future optimization)

---

## Trade-off Analysis

| Decision | Winner | Loser | Tradeoff |
|----------|--------|-------|----------|
| Backend | FastAPI | Node.js | AI/ML ecosystem vs deployment simplicity |
| Frontend | React+Vite | Next.js | iteration speed vs SSR |
| Database | Neon | Firebase | schema flexibility vs Realtime |
| State | Zustand | Redux | simplicity vs tooling |
| Validation | Pydantic | dataclasses | runtime checks vs stdlib |

---

## Future Decisions (Phase 5+)

- **ADR-021:** WebSocket streaming for progressive extraction
- **ADR-022:** Redis caching for frequently extracted tokens
- **ADR-023:** Migration to Next.js for SEO (if needed)
- **ADR-024:** Microservices for extraction types (Phase 7)
- **ADR-025:** Plugin system architecture

---

## References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
- [W3C Design Tokens](https://tr.designtokens.org/format/)
- [Pydantic v2 Docs](https://docs.pydantic.dev/latest/)
- [Zustand Docs](https://zustand-demo.pmnd.rs/)
