# Token Pipeline Planning Documentation

**Date Created:** 2025-11-22 | **Status:** Active Planning

This folder contains comprehensive implementation planning documents for the token pipeline system, including spacing token implementation and the reusable token factory abstraction.

---

## Documents

### 1. [SPACING_TOKEN_PIPELINE_PLANNING.md](./SPACING_TOKEN_PIPELINE_PLANNING.md)

**Purpose:** Comprehensive implementation plan for the spacing token pipeline

**Contents:**
- Architecture overview and data flow
- Pydantic and SQLAlchemy models
- AI extractor implementation details
- Utility functions for spacing computation
- Aggregation and deduplication strategy
- Async/parallel/streaming patterns
- API endpoints and schemas
- Database migration
- Testing strategy
- Frontend integration

**Key Features:**
- Follows proven color token patterns
- Supports parallel async batch processing
- SSE streaming for real-time progress
- Percentage-based deduplication (10% threshold)
- Multiple export formats (W3C, CSS, React, Tailwind)

---

### 2. [TOKEN_FACTORY_PLANNING.md](./TOKEN_FACTORY_PLANNING.md)

**Purpose:** Reusable abstraction/factory for creating future token types

**Contents:**
- Core factory architecture
- Abstract base classes (BaseToken, BaseExtractor, BaseAggregator, BaseGenerator)
- Registry system for plugin discovery
- Pipeline orchestrator
- Streaming engine
- Step-by-step template for new token types
- API router factory
- Testing infrastructure
- Frontend integration patterns

**Key Features:**
- Enables 80%+ code reuse between token types
- Plugin-style architecture
- Built-in parallel async processing
- Streaming support out of the box
- Consistent patterns across all token types
- Easy to add new token types (hours, not days)

---

## How These Documents Work Together

```
┌─────────────────────────────────┐
│   TOKEN_FACTORY_PLANNING.md     │
│   (Reusable Abstractions)       │
└─────────────┬───────────────────┘
              │
              │ extends
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐
│ Color │ │Spacing│ │ Typo  │
│ Token │ │ Token │ │ graphy│
└───────┘ └───────┘ └───────┘
              │
              │ documented in
              ▼
┌─────────────────────────────────┐
│ SPACING_TOKEN_PIPELINE_PLANNING │
│ (Concrete Implementation)       │
└─────────────────────────────────┘
```

---

## Implementation Order

### Recommended Approach

1. **First:** Implement Token Factory Core
   - Base classes and registry
   - Pipeline and streaming infrastructure

2. **Then:** Migrate Color Token
   - Refactor to use factory abstractions
   - Verify existing functionality

3. **Next:** Implement Spacing Token
   - Follow SPACING_TOKEN_PIPELINE_PLANNING.md
   - Use factory patterns

4. **Finally:** Add More Token Types
   - Typography, shadow, border, etc.
   - Each follows same pattern

---

## Key Design Principles

### 1. Parallel Async Processing
- Semaphore-controlled concurrency
- `asyncio.gather()` for parallel extraction
- Default 5 concurrent requests

### 2. Streaming Support
- Server-Sent Events (SSE)
- Real-time progress updates
- Phase-based extraction flow

### 3. Deduplication
- Configurable similarity thresholds
- Provenance tracking (which images contributed)
- Type-specific similarity measures

### 4. Plugin Architecture
- Registry-based discovery
- Loose coupling between components
- Easy to extend without modifying core

---

## Related Documentation

- [PLUGIN_ARCHITECTURE.md](../../architecture/PLUGIN_ARCHITECTURE.md) - Plugin system overview
- [EXTRACTOR_PATTERNS.md](../../architecture/EXTRACTOR_PATTERNS.md) - Extractor best practices
- [TOKEN_SYSTEM.md](../../domain/TOKEN_SYSTEM.md) - Token types and structure
- [MODULAR_TOKEN_PLATFORM_VISION.md](../../architecture/MODULAR_TOKEN_PLATFORM_VISION.md) - Platform vision

---

## Notes for Implementation

### Important Considerations

1. **Do not touch actual code** - These are planning documents only
2. **Parallel development** - Multiple token types can be built simultaneously
3. **Streaming is critical** - Users expect real-time progress feedback
4. **Testing first** - Base test classes enable comprehensive coverage

### Branch Integration

These documents should be used alongside documentation from other concurrent branches. Additional context is available in:

**Available Now:**
- `origin/claude/backend-optimization-01HdBkJYq9u3qUWwuZc3pHnC` - Backend systems architecture analysis
  - AI/ML Pipeline (Claude/OpenAI integration, prompt engineering)
  - Database & Performance (indexing, N+1 queries)
  - Security & Authentication
  - See `docs/backend-analysis/` in that branch

- `origin/claude/cv-preprocessing-pipeline-01D2oeMjGQwu6Yk35cyr8XK6` - CV preprocessing for extraction
- `origin/claude/frontend-infrastructure-eval-01DFv28F3rgKhqvgGRRyxvhW` - Frontend infrastructure

**May Be Created Soon:**
- Typography token planning
- Shadow/border token planning
- Additional architecture documentation

Check other branches periodically (every 10-20 minutes) for updates that may inform implementation.

---

**Maintained by:** Claude Code Planning Agent
**Last Updated:** 2025-11-22
