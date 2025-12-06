# Shadow Tokens Implementation Plan

**Timeline:** 1-2 days
**Complexity:** Low (reuse CV patterns + existing ShadowExtractor structure)
**Status:** In Progress

---

## 🎯 Goals

- [ ] Implement real shadow detection from UI images
- [ ] Create `ShadowToken` database model
- [ ] Build extraction → database → token graph pipeline
- [ ] Add `/api/v1/shadows/extract` endpoint
- [ ] Write 15+ comprehensive tests
- [ ] Integrate with W3C export

---

## 📋 Implementation Checklist

### Phase 1: Database & Models

- [ ] Add `ShadowToken` class to `domain/models.py`
  - Fields: `x`, `y`, `blur`, `spread`, `color_hex`, `opacity`, `semantic_name`, `confidence`
  - Relations: `project_id`, `extraction_job_id`
  - Follow ColorToken/SpacingToken pattern

- [ ] Create Alembic migration: `add_shadow_tokens_table.py`

### Phase 2: Shadow Extraction

- [ ] Enhance `AIShadowExtractor` (currently in `color_extractor.py`)
  - Implement shadow detection via Claude vision
  - Extract: x, y, blur, spread, color, opacity
  - Return: `ExtractedShadowToken` dataclass with confidence scores

- [ ] Keep existing `ShadowExtractor` for W3C schema generation

### Phase 3: Service Layer

- [ ] Create `services/shadow_service.py`
  - `db_shadows_to_repo()`: Load shadows from DB into TokenRepository
  - `build_shadow_repo_from_db()`: Aggregate shadows with deduplication
  - `extract_and_store_shadows()`: Extract → DB → graph pipeline

### Phase 4: API Implementation

- [ ] Update `interfaces/api/shadows.py`
  - Implement `POST /api/v1/shadows/extract` (real extraction)
  - Implement `GET /api/v1/shadows/{id}` (retrieve shadow)
  - Replace stub `/api/v1/shadows` with real endpoint

### Phase 5: Testing

- [ ] Unit tests: `test_shadow_extraction.py` (8 tests)
  - Test shadow detection accuracy
  - Test deduplication logic
  - Test edge cases (no shadows, overlapping shadows, etc.)

- [ ] API tests: `test_shadows_api.py` (7 tests)
  - Test `/shadows/extract` endpoint
  - Test `/shadows/{id}` endpoint
  - Test error handling

- [ ] Integration tests: `test_shadow_integration.py` (3 tests)
  - Extract → DB → Graph → W3C export

### Phase 6: Documentation

- [ ] Update API docs
- [ ] Add shadow token examples
- [ ] Document W3C mapping

---

## 📁 Files to Create/Modify

### Create

```
src/copy_that/application/ai_shadow_extractor.py        NEW (shadow detection)
src/copy_that/services/shadow_service.py                NEW (service layer)
src/copy_that/alembic/versions/add_shadow_tokens.py     NEW (migration)
tests/unit/services/test_shadow_service.py              NEW (unit tests)
tests/unit/api/test_shadows_api.py                      NEW (API tests)
```

### Modify

```
src/copy_that/domain/models.py                          ADD ShadowToken class
src/copy_that/interfaces/api/shadows.py                 UPDATE endpoints
src/copy_that/application/color_extractor.py            EXTEND for shadows
```

---

## 🔄 Data Flow

```
Image
  ↓
AIShadowExtractor.extract() → ExtractedShadowToken[]
  ↓
shadow_service.extract_and_store_shadows()
  ├─ Database: ShadowToken rows
  ├─ TokenRepository: shadow tokens with relations
  └─ GraphRelations: color token references (COMPOSES)
  ↓
W3C Adapter
  ↓
Output: W3C JSON with shadows
```

---

## 🧪 Test Strategy

### Unit Tests (Shadow Extraction)
```python
test_detect_shadows_single_layer()
test_detect_shadows_multiple_layers()
test_shadow_deduplication()
test_shadow_color_reference()
test_shadow_edge_cases_no_shadows()
test_shadow_edge_cases_extreme_values()
test_shadow_w3c_schema_generation()
test_shadow_confidence_scoring()
```

### API Tests (Endpoints)
```python
test_extract_shadows_from_image()
test_extract_shadows_from_base64()
test_get_shadow_by_id()
test_shadows_extraction_with_rate_limiting()
test_shadows_invalid_project_id_404()
test_shadows_missing_image_400()
test_shadows_export_w3c()
```

### Integration Tests
```python
test_shadow_extraction_end_to_end()
test_shadows_in_token_graph()
test_shadows_w3c_export_integration()
```

---

## 💻 Key Prompts for Claude

### For Shadow Detection Algorithm
```
In AIShadowExtractor, implement shadow detection using Claude vision:
- Analyze UI screenshot for drop shadows, inner shadows, text shadows
- Extract: x offset, y offset, blur radius, spread radius, color, opacity
- Calculate confidence scores based on shadow clarity
- Handle edge cases: no shadows, multiple layers, semi-transparent backgrounds
- Return ExtractedShadowToken with all properties
```

### For Database Model
```
Create ShadowToken model following ColorToken/SpacingToken pattern:
- Minimal fields: x, y, blur, spread, color_hex, opacity, confidence
- Foreign keys: project_id, extraction_job_id (like colors/spacing)
- Timestamps: created_at
- String fields for naming/semantic roles (optional)
```

### For Service Integration
```
Build shadow_service.py following colors_service.py structure:
- db_shadows_to_repo(): Load shadows from DB into TokenRepository
- extract_and_store_shadows(): Full extraction pipeline
- aggregate_shadow_batch(): Deduplication with similarity threshold
```

---

## ⏱️ Time Breakdown

- ShadowToken model: 15 min
- Migration: 10 min
- AIShadowExtractor: 30 min
- shadow_service.py: 25 min
- API endpoints: 20 min
- Tests: 40 min
- **Total: ~2-2.5 hours**

---

## 🎯 Definition of Done

- [ ] ShadowToken model created and migrated
- [ ] AIShadowExtractor implemented with real detection
- [ ] `/api/v1/shadows/extract` endpoint returns real shadows
- [ ] 15+ tests passing (8 unit + 7 API)
- [ ] W3C export includes shadows
- [ ] Token graph has shadow tokens with color references
- [ ] Documentation updated
- [ ] All tests passing: `pytest tests/ -v --tb=short`

---

## 📊 Success Metrics

- **Coverage:** Shadows move from 20% → 80% complete
- **Tests:** 50+ → 65+ total tests passing
- **API Endpoints:** 6 → 7 (add /shadows/extract)
- **Token Types Ready:** 2 → 2.5/8

---
