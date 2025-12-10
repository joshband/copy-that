# Reorganization Plan: application/ → extractors/

**Goal:** Move from flat messy structure to modular zero-coupling architecture

**Scope:** 15 extractor files + utility files = ~30 imports to update

---

## Current Structure (Before)

```
src/copy_that/application/
├── color_extractor.py
├── openai_color_extractor.py
├── ai_typography_extractor.py
├── ai_shadow_extractor.py
├── cv_shadow_extractor.py
├── color_clustering.py
├── color_utils.py (48KB!)
├── color_spaces_advanced.py
├── semantic_color_naming.py
├── spacing_extractor.py
├── spacing_utils.py
├── spacing_models.py
├── shadow_extractor.py
├── batch_extractor.py
├── multimodal_orchestrator.py
├── cv/
│   ├── color_cv_extractor.py
│   ├── spacing_cv_extractor.py
│   └── typography_cv_extractor.py
├── tests/
└── ... other files
```

---

## New Structure (After)

```
src/copy_that/extractors/
├── __init__.py                    # Registry pattern
├── base.py                        # BaseExtractor abstract class
│
├── color/
│   ├── __init__.py
│   ├── extractor.py              # ColorExtractor
│   ├── openai_extractor.py        # OpenAIColorExtractor
│   ├── clustering.py              # ColorKMeans logic
│   ├── utils.py                   # Color-specific utilities
│   ├── color_spaces.py            # Advanced color space logic
│   └── semantic_naming.py          # Semantic color naming
│
├── spacing/
│   ├── __init__.py
│   ├── extractor.py              # SpacingExtractor
│   ├── cv_extractor.py           # SpacingCVExtractor
│   ├── models.py                 # Spacing data models
│   └── utils.py                  # Spacing utilities
│
├── typography/
│   ├── __init__.py
│   ├── extractor.py              # TypographyExtractor
│   ├── cv_extractor.py           # TypographyCVExtractor
│   ├── ai_extractor.py           # AITypographyExtractor
│   └── recommender.py            # Typography recommendations
│
├── shadow/
│   ├── __init__.py
│   ├── extractor.py              # ShadowExtractor
│   ├── cv_extractor.py           # ShadowCVExtractor
│   └── ai_extractor.py           # AIShadowExtractor
│
└── orchestrator.py               # MultimodalOrchestrator (uses registry)
```

---

## Migration Steps

### Phase 1: Create New Structure (10 min)

```bash
mkdir -p src/copy_that/extractors/{color,spacing,typography,shadow}
touch src/copy_that/extractors/__init__.py
touch src/copy_that/extractors/base.py
touch src/copy_that/extractors/{color,spacing,typography,shadow}/__init__.py
```

### Phase 2: Move Color Files (15 min)

```
color_extractor.py                → extractors/color/extractor.py
openai_color_extractor.py         → extractors/color/openai_extractor.py
color_clustering.py               → extractors/color/clustering.py
color_utils.py (color parts)      → extractors/color/utils.py
color_spaces_advanced.py          → extractors/color/color_spaces.py
semantic_color_naming.py          → extractors/color/semantic_naming.py
cv/color_cv_extractor.py          → extractors/color/cv_extractor.py
```

### Phase 3: Move Spacing Files (10 min)

```
spacing_extractor.py              → extractors/spacing/extractor.py
spacing_utils.py                  → extractors/spacing/utils.py
spacing_models.py                 → extractors/spacing/models.py
cv/spacing_cv_extractor.py        → extractors/spacing/cv_extractor.py
```

### Phase 4: Move Typography Files (10 min)

```
ai_typography_extractor.py        → extractors/typography/ai_extractor.py
typography_recommender.py         → extractors/typography/recommender.py
cv/typography_cv_extractor.py     → extractors/typography/cv_extractor.py
```

### Phase 5: Move Shadow Files (5 min)

```
shadow_extractor.py               → extractors/shadow/extractor.py
ai_shadow_extractor.py            → extractors/shadow/ai_extractor.py
cv_shadow_extractor.py            → extractors/shadow/cv_extractor.py
```

### Phase 6: Create Base Class & Registry (20 min)

Create `src/copy_that/extractors/base.py`:
```python
from abc import ABC, abstractmethod
from core.tokens.model import Token

class BaseExtractor(ABC):
    token_type: str = "unknown"

    @abstractmethod
    async def extract(self, input_data: str | bytes) -> list[Token]:
        pass
```

Create `src/copy_that/extractors/__init__.py` with registry:
```python
from extractors.color import ColorExtractor, OpenAIColorExtractor
from extractors.spacing import SpacingExtractor
# ... import all extractors

EXTRACTORS = {
    "color": ColorExtractor,
    "spacing": SpacingExtractor,
    ...
}

def get_extractor(token_type: str):
    return EXTRACTORS[token_type]()
```

### Phase 7: Update Imports (30 min)

Files to update:
1. `src/copy_that/services/colors_service.py`
2. `src/copy_that/services/spacing_service.py`
3. `src/copy_that/services/shadow_service.py`
4. `src/copy_that/services/typography_service.py`
5. `src/copy_that/interfaces/api/colors.py`
6. `src/copy_that/interfaces/api/spacing.py`
7. `src/copy_that/interfaces/api/typography.py`
8. `src/copy_that/interfaces/api/shadows.py`
9. `src/copy_that/interfaces/api/multi_extract.py`
10. `src/copy_that/interfaces/api/design_tokens.py`
11. `src/copy_that/interfaces/api/sessions.py`
12. `src/copy_that/tokens/color/aggregator.py`
13. `src/copy_that/tokens/spacing/aggregator.py`
14. Test files (13 files)
15. `pipeline/panel_to_tokens.py`

### Phase 8: Test & Verify (15 min)

```bash
pnpm typecheck
curl http://localhost:8000/docs
# Test a color extraction endpoint
```

### Phase 9: Commit (5 min)

```bash
git add -A
git commit -m "refactor: Reorganize application/ to modular extractors/ architecture

- Move color extractors to extractors/color/
- Move spacing extractors to extractors/spacing/
- Move typography extractors to extractors/typography/
- Move shadow extractors to extractors/shadow/
- Create BaseExtractor abstraction
- Implement registry pattern for zero coupling
- Update all imports across 15+ files

Benefits:
✓ Clear module boundaries
✓ Easy to add new token types
✓ Enable parallel development
✓ Reduce file sizes (color_utils 48KB → 5KB chunks)
✓ Foundation for Phase 1 streaming
"
```

---

## Timeline

- **Phase 1-5 (File moves):** 50 min
- **Phase 6 (Base + Registry):** 20 min
- **Phase 7 (Update imports):** 30 min
- **Phase 8 (Test):** 15 min
- **Phase 9 (Commit):** 5 min

**Total: ~2 hours**

---

## Risk Assessment

**Low Risk Because:**
- Only moving files (no logic changes)
- All imports will be updated before testing
- Backend already running, easy to verify nothing broke
- Can rollback with git if needed

**Verification Points:**
1. ✅ `pnpm typecheck` passes
2. ✅ Backend API responds (curl /docs)
3. ✅ Sample color extraction works
4. ✅ No import errors in test files

---

## Expected Benefits

✅ **Code Organization**
- Color logic in one place
- Spacing logic in one place
- etc.

✅ **Maintainability**
- Easy to find what you need
- Clear boundaries

✅ **Extensibility**
- Add new extractor type in 1 directory
- Registry automatically picks it up

✅ **Foundation for Phase 1**
- Streaming endpoint will use registry
- Generators will use registry
- No coupling between modules

---

## Do Not Delete During Migration

- Keep `application/` directory (other code may still reference it temporarily)
- Keep old imports working during transition
- Add deprecation notice if needed

---

**Ready to execute? Start with Phase 1.**
