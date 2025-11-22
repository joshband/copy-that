# CV Preprocessing Pipeline - Implementation Plan

**Document Version:** 1.0
**Date:** 2025-11-22
**Author:** Computer Vision & Image Processing Specialist
**Status:** Design Document - Do Not Implement Yet

---

## Executive Summary

This documentation set provides a comprehensive plan for implementing a production-ready Computer Vision preprocessing pipeline for the **copy-that** platform. The pipeline will prepare images optimally before AI-based color extraction, improving reliability, performance, and cost efficiency.

### Key Objectives

- **Security:** Prevent SSRF, validate file types, enforce size limits
- **Performance:** Async operations, connection pooling, concurrent processing
- **Reliability:** Graceful degradation, comprehensive error handling
- **Cost Optimization:** Preprocessed images reduce AI API costs by 40-60%

### Estimated Impact

| Metric | Before | After |
|--------|--------|-------|
| Average image size to API | 2.5MB | 500KB |
| Processing failures | ~5% | <0.5% |
| API cost per extraction | Baseline | -40-60% |
| Docker image size | ~600MB | ~660MB (+10%) |

---

## Document Index

| # | Document | Description |
|---|----------|-------------|
| 1 | [Current State Assessment](./01-current-state-assessment.md) | Audit of existing capabilities, dependencies, gaps, and risks |
| 2 | [OpenCV Pipeline Design](./02-opencv-pipeline-design.md) | Architecture, preprocessing steps, memory optimization |
| 3 | [Async Loading Strategy](./03-async-loading-strategy.md) | httpx integration, aiofiles, connection pooling, concurrency |
| 4 | [Validation & Error Handling](./04-validation-error-handling.md) | Magic byte detection, size limits, corrupt image handling |
| 5 | [Dependency Recommendations](./05-dependency-recommendations.md) | Updated pyproject.toml, justifications, conflict analysis |
| 6 | [Unit Testing Strategy](./06-unit-testing-strategy.md) | Test cases, mocks, fixtures, performance benchmarks |
| 7 | [Implementation Roadmap](./07-implementation-roadmap.md) | Phased rollout plan with detailed tasks |
| 8 | [Documentation Plan](./08-documentation-plan.md) | API docs, examples, troubleshooting, performance tuning |

---

## Quick Reference

### New Files to Create

```
src/copy_that/
├── infrastructure/
│   └── cv/
│       ├── __init__.py
│       ├── preprocessing.py      # Main pipeline orchestrator
│       ├── loader.py             # Async image loading
│       ├── validator.py          # Image validation
│       ├── preprocessor.py       # OpenCV operations
│       ├── optimizer.py          # Compression & format conversion
│       ├── exceptions.py         # Custom exceptions
│       └── config.py             # Pipeline configuration
│
└── application/
    └── services/
        └── image_service.py      # High-level service API

tests/unit/test_image_processing/
├── __init__.py
├── conftest.py
├── test_loader.py
├── test_validator.py
├── test_preprocessor.py
├── test_optimizer.py
├── test_pipeline.py
└── fixtures/
```

### New Dependencies

```toml
# Add to pyproject.toml [project.dependencies]
"opencv-python-headless>=4.9.0",
"httpx[http2]>=0.27.0",
"aiofiles>=23.2.0",
"python-magic>=0.4.27",
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CV_MAX_FILE_SIZE_MB` | 20.0 | Maximum upload file size |
| `CV_MAX_DIMENSION` | 4096 | Maximum input dimension |
| `CV_TARGET_DIMENSION` | 2048 | Output resize target |
| `CV_MAX_CONCURRENT` | 4 | Concurrent operations |
| `CV_OUTPUT_FORMAT` | webp | Output format |
| `CV_ENABLE_ENHANCEMENT` | true | Enable CLAHE enhancement |

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   URL/File/     │     │    Validation   │     │  Preprocessing  │
│   Base64 Input  │ ──► │    Pipeline     │ ──► │    Pipeline     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                       │
        ▼                        ▼                       ▼
   ┌─────────┐            ┌─────────────┐         ┌─────────────┐
   │  httpx  │            │ python-magic│         │   OpenCV    │
   │ aiofiles│            │   Pillow    │         │   Pillow    │
   └─────────┘            └─────────────┘         └─────────────┘
                                                         │
                                                         ▼
                                                  ┌─────────────┐
                                                  │ Optimized   │
                                                  │ Image (WebP)│
                                                  └─────────────┘
                                                         │
                                                         ▼
                                                  ┌─────────────┐
                                                  │ AI Color    │
                                                  │ Extraction  │
                                                  └─────────────┘
```

---

## Implementation Phases

### Phase 1: Core Dependencies & Basic Loading
- Add dependencies to pyproject.toml
- Implement async loading (httpx, aiofiles)
- Implement basic validation
- Initial unit tests

### Phase 2: Preprocessing Pipeline
- OpenCV preprocessing operations
- Image optimization
- Pipeline orchestration
- Application service integration

### Phase 3: Optimization & Production
- Memory optimization for Cloud Run
- Optional caching layer
- Production hardening
- Documentation

---

## Constraints

### DO NOT Modify
- API endpoints
- Database models
- Frontend code
- Existing infrastructure configs

### DO
- Create new infrastructure/cv/ module
- Add new application service
- Add new dependencies
- Create comprehensive tests

---

## Getting Started

1. **Review Current State**: Start with [01-current-state-assessment.md](./01-current-state-assessment.md)
2. **Understand Architecture**: Read [02-opencv-pipeline-design.md](./02-opencv-pipeline-design.md)
3. **Check Dependencies**: Review [05-dependency-recommendations.md](./05-dependency-recommendations.md)
4. **Plan Implementation**: Follow [07-implementation-roadmap.md](./07-implementation-roadmap.md)

---

*This documentation set was prepared for the copy-that platform. Do not implement without approval.*
