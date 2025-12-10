# Reorganization Status - 2025-12-10

**Date:** 2025-12-10 (this session)
**Status:** 70% complete - directories/files moved, registries created, imports need fixing
**Token Usage:** ~115K/200K (continuing from previous session clear)

---

## What's Done ✅

### Phase 1-5: File Movement (Complete)
- ✅ Created `src/copy_that/extractors/` directory structure
- ✅ Created subdirectories: `color/`, `spacing/`, `typography/`, `shadow/`
- ✅ Copied all 17 extractor files to new locations:
  - Color: 6 files (extractor, openai_extractor, clustering, color_spaces, semantic_naming, cv_extractor)
  - Spacing: 4 files (extractor, cv_extractor, utils, models)
  - Typography: 3 files (ai_extractor, recommender, cv_extractor)
  - Shadow: 3 files (extractor, ai_extractor, cv_extractor)
  - Multimodal: 1 file (orchestrator)

### Phase 6: Registry & Base Classes (Partial)
- ✅ Created `src/copy_that/extractors/__init__.py` with:
  - Registry pattern (get_extractor, register_extractor)
  - Lazy loading of extractors
  - Type hints for all extractor types
- ✅ Created `__init__.py` files for:
  - `color/` ✅
  - `spacing/` ✅
  - `typography/` ✅
  - `shadow/` ✅

### Architecture Documents Created
- ✅ `REORGANIZATION_PLAN.md` - Detailed step-by-step plan
- ✅ `ARCHITECTURE_DIAGRAMS.md` - Mermaid visualizations (10 diagrams)

---

## What's Remaining ❌

### Phase 7: Fix Imports (30-45 min work)

**Files needing import updates:**
1. **Extractors (17 files):**
   - `extractors/color/extractor.py` - imports from `application.color_utils`, `application.semantic_color_naming`
   - `extractors/color/openai_extractor.py` - similar imports
   - `extractors/spacing/extractor.py` - imports from `application.spacing_utils`
   - `extractors/typography/ai_extractor.py` - imports from `application`
   - `extractors/shadow/extractor.py` - imports from `application`

2. **Services (4 files):**
   - `services/colors_service.py` - update imports
   - `services/spacing_service.py` - update imports
   - `services/typography_service.py` - update imports
   - `services/shadow_service.py` - update imports

3. **API Routes (6 files):**
   - `interfaces/api/colors.py`
   - `interfaces/api/spacing.py`
   - `interfaces/api/typography.py`
   - `interfaces/api/shadows.py`
   - `interfaces/api/multi_extract.py`
   - `interfaces/api/design_tokens.py`

4. **Other (3 files):**
   - `tokens/color/aggregator.py`
   - `tokens/spacing/aggregator.py`
   - Test files in `application/tests/`

**Import Fix Strategy:**

**Option A: Keep application/ as-is (Safest)**
```python
# In extractors/color/extractor.py
from copy_that.application import color_utils  # KEEP as-is
from copy_that.application.semantic_color_naming import analyze_color  # KEEP as-is
```
- No changes to application/ files
- Extractors still work through application/
- Later phase: split utils incrementally

**Option B: Move utils to extractors/ (Cleaner)**
```python
# Copy/split color_utils.py → extractors/color/utils.py
# Copy semantic_color_naming.py → extractors/color/semantic_naming.py
# Update all imports to relative
from .utils import color_utility_function
from .semantic_naming import analyze_color
```
- More work now (~2 hours)
- Cleaner structure
- True modularity

**RECOMMENDATION:** Use **Option A** for now:
- Services/API can start using registry immediately: `from copy_that.extractors import get_extractor`
- Extractors work even with old imports
- Phase out old structure gradually

### Phase 8: Create BaseExtractor (10 min)

Create `src/copy_that/extractors/base.py`:
```python
from abc import ABC, abstractmethod
from core.tokens.model import Token

class BaseExtractor(ABC):
    """Base class for all token extractors."""

    token_type: str = "unknown"

    @abstractmethod
    async def extract(self, input_data: str | bytes) -> list[Token]:
        """Extract tokens from input data."""
        pass

    async def preprocess(self, data: str | bytes) -> str | bytes:
        """Optional preprocessing hook."""
        return data

    async def postprocess(self, tokens: list[Token]) -> list[Token]:
        """Optional postprocessing hook."""
        return tokens
```

Then update extractors to inherit from BaseExtractor.

### Phase 9: Update Service Imports (30 min)

Update only the critical files:
```python
# OLD:
from copy_that.application.color_extractor import ColorExtractor

# NEW:
from copy_that.extractors import get_extractor
extractor = get_extractor("color")
```

This enables services to work with the new registry pattern.

### Phase 10: Test & Verify (15 min)

```bash
# Check backend still runs
curl http://localhost:8000/docs

# Run typecheck
pnpm typecheck

# Test a color extraction endpoint
curl -X POST http://localhost:8000/api/v1/colors/extract \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "..."}'
```

### Phase 11: Commit (5 min)

```bash
git add -A
git commit -m "refactor: Reorganize application/ to modular extractors/ architecture

- Created extractors/ directory with color/, spacing/, typography/, shadow/ subdirs
- Moved 17 extractor files to appropriate modules
- Implemented registry pattern for zero coupling
- Created __init__.py files for all modules
- Extractors can be accessed via get_extractor() registry

Import compatibility:
- Old imports still work through application/
- Services can migrate to new registry gradually
- Extractors use relative imports where possible

Next: Fix extractor imports to use relative paths
Next: Update services/API to use registry pattern
"
```

---

## Critical Files Locations (After Reorganization)

```
src/copy_that/
├── extractors/                    ← NEW
│   ├── __init__.py               (registry pattern)
│   ├── base.py                   (BaseExtractor - needs creation)
│   ├── color/
│   │   ├── __init__.py
│   │   ├── extractor.py          (moved from application/)
│   │   ├── openai_extractor.py   (moved)
│   │   ├── clustering.py         (moved from color_clustering.py)
│   │   ├── color_spaces.py       (moved from color_spaces_advanced.py)
│   │   ├── semantic_naming.py    (moved from semantic_color_naming.py)
│   │   └── cv_extractor.py       (moved from cv/color_cv_extractor.py)
│   ├── spacing/
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   ├── cv_extractor.py
│   │   ├── utils.py
│   │   └── models.py
│   ├── typography/
│   │   ├── __init__.py
│   │   ├── ai_extractor.py
│   │   ├── recommender.py
│   │   └── cv_extractor.py
│   └── shadow/
│       ├── __init__.py
│       ├── extractor.py
│       ├── ai_extractor.py
│       └── cv_extractor.py
│
├── application/                   ← OLD (still exists)
│   ├── __init__.py
│   ├── color_extractor.py        (OLD - can delete after migration)
│   ├── color_utils.py            (utilities used by extractors)
│   ├── semantic_color_naming.py  (utilities)
│   └── ... (other application code)
│
├── services/
│   ├── colors_service.py         ← needs import updates
│   ├── spacing_service.py        ← needs import updates
│   ├── typography_service.py     ← needs import updates
│   └── shadow_service.py         ← needs import updates
│
└── interfaces/api/
    ├── colors.py                 ← needs import updates
    ├── spacing.py                ← needs import updates
    └── ... (other routes)
```

---

## Testing Checklist for Next Session

- [ ] Backend starts without errors: `curl http://localhost:8000/docs`
- [ ] Registry loads all extractors: check logs
- [ ] Color extraction works: test API endpoint
- [ ] Typecheck passes: `pnpm typecheck`
- [ ] No import errors in services
- [ ] No import errors in API routes

---

## Benefits After Completion

✅ **Code Organization** - Each token type in its own directory
✅ **Zero Coupling** - Modules are independent, use registry pattern
✅ **Easy Extensions** - Add new token type in 1 directory
✅ **Foundation for Phase 1** - Streaming endpoint will use registry
✅ **Scalability** - Foundation for multi-framework generators

---

## Files Status

### Moved (17 extractor files)
✅ Copied to new locations
⚠️ Need import fixes (10-15 files)
⚠️ Need relative import updates

### Created (10 new files)
✅ `src/copy_that/extractors/__init__.py` (registry)
✅ `src/copy_that/extractors/color/__init__.py`
✅ `src/copy_that/extractors/spacing/__init__.py`
✅ `src/copy_that/extractors/typography/__init__.py`
✅ `src/copy_that/extractors/shadow/__init__.py`
⚠️ `src/copy_that/extractors/base.py` (needs creation)

### Unchanged (kept for compatibility)
✅ `src/copy_that/application/` (old files still there)

---

## Implementation Priority (Next Session)

1. **Quick Win (10 min):** Create BaseExtractor in extractors/base.py
2. **Fix Imports (30 min):** Update extractors to use relative imports for utilities
3. **Update Services (20 min):** Change services to use get_extractor() registry
4. **Update API Routes (20 min):** Change API routes to use registry
5. **Test Everything (15 min):** Verify backend, typecheck, API endpoints work
6. **Commit (5 min):** Clean, organized commit

**Total Time Next Session:** 1.5-2 hours

---

## Code Example: Using the New Registry

**Old way (deprecated but still works):**
```python
from copy_that.application.color_extractor import ColorExtractor
extractor = ColorExtractor()
colors = await extractor.extract(image_data)
```

**New way (using registry):**
```python
from copy_that.extractors import get_extractor
extractor = get_extractor("color")
colors = await extractor.extract(image_data)
```

**Benefits:**
- Services don't know about specific extractors
- Adding new extractor only requires registry entry
- Can swap implementations without changing services
- Foundation for streaming/generators

---

## Next Session Checklist

- [ ] Review this document
- [ ] Create BaseExtractor
- [ ] Fix imports in 10-15 files
- [ ] Test backend
- [ ] Commit changes
- [ ] Ready for Phase 1 streaming implementation

---

**This reorganization is the foundation for everything else. Once complete, Phase 1 (streaming) and Phase 2+ (multi-framework generators) become straightforward.**
