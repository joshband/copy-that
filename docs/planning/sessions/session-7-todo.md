# Session 7: Spacing Tokens & Next Steps

**Status:** TODO - Next Implementation Phase

---

## Overview

With the pipeline architecture complete (Sessions 0-6), the next phase focuses on implementing spacing tokens as the second token type, followed by documentation consolidation and security hardening.

---

## Priority 1: Spacing Token Implementation (Weeks 2-4)

### Week 2: Foundation

#### 1. Review & Design (4h)
- [ ] Review spacing token planning docs in `docs/planning/token-pipeline-planning/`
- [ ] Design spacing extractor interface
- [ ] Define spacing-specific Tool Use schema

#### 2. Domain Models (3h)
- [ ] Add spacing to `TokenType` enum
- [ ] Create spacing Pydantic models
- [ ] Add spacing to `W3CTokenType` (dimension type)

#### 3. Extraction Schema (4h)
- [ ] Add spacing schema to `src/copy_that/pipeline/extraction/schemas.py`
- [ ] Create spacing prompt template in `prompts.py`
- [ ] Write tests FIRST

### Week 3: Integration

#### 4. Generators (3h)
- [ ] Add spacing to W3C template (`templates/w3c.j2`)
- [ ] Add CSS spacing variables (`templates/css.j2`)
- [ ] Add React spacing theme (`templates/react.j2`)
- [ ] Add Tailwind spacing config (`templates/tailwind.j2`)

#### 5. Frontend Component (3h)
- [ ] Create SpacingDisplay component
- [ ] Integrate spacing into TokenGrid
- [ ] Add spacing to Inspector view

#### 6. API Endpoint (3h)
- [ ] Add `/api/v1/spacing/extract` endpoint
- [ ] Update batch extraction to include spacing

### Week 4: Testing & Polish

#### 7. Testing (4h)
- [ ] Unit tests for spacing extraction
- [ ] Integration tests for full pipeline
- [ ] E2E test: upload → extract → export

#### 8. Documentation (2h)
- [ ] Update README with spacing examples
- [ ] Add spacing curl examples to `docs/examples/`
- [ ] Update architecture docs

---

## Priority 2: Quick Wins (1-2 days each)

### Redis Caching for Extractions
- [ ] Implement cache by image hash
- [ ] Add cache invalidation strategy
- [ ] Estimated 70% cost reduction on repeat extractions

### Multi-Token Extraction
- [ ] Extract multiple token types in single API call
- [ ] Reduce API costs from ~$0.75/image to ~$0.03/image
- [ ] Batch 5 types per call

---

## Priority 3: Documentation Consolidation (Week 5)

### Roadmap Consolidation
- [ ] Merge `docs/planning/2025-11-21-roadmap.md` and `docs/overview/strategy/2025-11-20_roadmap.md`
- [ ] Create single `ROADMAP.md` in repo root
- [ ] Archive old session notes

### Master Index Update
- [ ] Update `docs/overview/documentation.md` with all new sections
- [ ] Add CV Preprocessing Pipeline (8 docs)
- [ ] Add Frontend Infrastructure Analysis (6 docs)
- [ ] Add Spacing Token Planning (5+ docs)

### Cross-Reference Fixes
- [ ] Scan for broken internal links
- [ ] Ensure all docs have "Last Updated" dates
- [ ] Create unified testing index

---

## Priority 4: v0.5.0 Release (Week 6)

### Pre-Release
- [ ] Final test suite run
- [ ] Update CHANGELOG for v0.5.0
- [ ] Version bump in pyproject.toml

### Deployment
- [ ] Deploy to staging
- [ ] Staging verification checklist
- [ ] Deploy to production
- [ ] Production smoke tests

### Post-Release
- [ ] Tag v0.5.0 in git
- [ ] Update examples with spacing
- [ ] Announce release

---

## Priority 5: Security Branch Preparation (Weeks 7-8)

### Conflict Resolution
- [ ] Resolve `main.py` merge conflict
- [ ] Resolve `sessions.py` merge conflict
- [ ] Run full test suite on resolved branch

### Testing
- [ ] Test Alembic migrations locally (up and down)
- [ ] Write rollback procedures
- [ ] Create merge PR (staging only)

### Staging Deployment
- [ ] Merge security branch to main
- [ ] Deploy to staging
- [ ] Test auth flow e2e (register → login → token refresh → logout)
- [ ] Test rate limiting behavior
- [ ] Test Redis failure modes
- [ ] Load testing with k6

**Note:** Production security deployment deferred to Phase 6

---

## Technical Approach for Spacing Tokens

### Hybrid CV/AI Method

```python
# 1. OpenCV for pixel measurements
edges = cv2.Canny(gray, 50, 150)
contours = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 2. Claude for semantic classification
tool_schema = {
    "name": "report_spacing_tokens",
    "input_schema": {
        "properties": {
            "spacings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "value": {"type": "number"},
                        "unit": {"enum": ["px", "rem", "em"]},
                        "context": {"enum": ["margin", "padding", "gap"]}
                    }
                }
            }
        }
    }
}
```

### Essential Preprocessing
- Grayscale conversion
- Bilateral filtering (noise reduction)
- CLAHE contrast enhancement
- Edge detection (Canny)

---

## Files to Create/Modify

### New Files
```
src/copy_that/pipeline/extraction/schemas.py  # Add spacing schema
src/copy_that/pipeline/generator/templates/spacing-*.j2
frontend/src/components/SpacingDisplay.tsx
tests/unit/pipeline/extraction/test_spacing.py
docs/examples/spacing_curl.md
```

### Modified Files
```
src/copy_that/pipeline/types.py  # Add spacing to enums
src/copy_that/pipeline/extraction/prompts.py  # Add spacing prompt
src/copy_that/interfaces/api/main.py  # Add spacing endpoint
README.md  # Add spacing examples
CHANGELOG.md  # Document v0.5.0
```

---

## Success Criteria

### Week 4 Checkpoint
- [ ] Spacing extraction working end-to-end
- [ ] All output formats support spacing
- [ ] Frontend displays spacing tokens
- [ ] 95%+ test coverage on spacing code

### Week 6 (v0.5.0 Release)
- [ ] Production deployment successful
- [ ] Health checks passing
- [ ] Spacing token extraction working in production
- [ ] Documentation complete

### Week 8 (Security Staging)
- [ ] Security merged to main
- [ ] Staging deployment successful
- [ ] Auth flow works completely
- [ ] Rate limiting triggers correctly
- [ ] Load test results documented

---

## Deferred to Phase 6

- Production security deployment
- Auth UI components
- Typography tokens
- Full CV preprocessing pipeline
- Additional token types (shadows, gradients, animations)

---

## References

- [PROJECT_IMPLEMENTATION_PLAN_AND_INTEGRATION_ROADMAP.md](../PROJECT_IMPLEMENTATION_PLAN_AND_INTEGRATION_ROADMAP.md)
- [SESSIONS_0-6_SUMMARY.md](../SESSIONS_0-6_SUMMARY.md)
- [Spacing Token Planning](../../planning/token-pipeline-planning/) (if exists)

---

*Next milestone: v0.5.0 with spacing tokens - Ship product value first!*
