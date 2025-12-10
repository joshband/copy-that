# Architecture Quick Reference

**Use this document as your daily reference for architecture decisions.**

---

## TL;DR

- **TokenGraph is the center** - all tokens, all relationships, all exports flow through it
- **Zero-coupling via registries** - extractors/exporters registered once, used everywhere
- **Generic Token type** - not ColorToken, SpacingToken, etc. Just Token + TokenType enum
- **Modular = add feature = 1 new module** - no touching existing code

---

## Decision Tree

### "Should this be a separate module?"

```
Does this extract/export tokens?
├─ YES → Create src/copy_that/extractors/[type]/ or src/copy_that/exporters/[type]/
└─ NO  → Belongs in domain, services, or infrastructure

Is it a pure algorithm (no token logic)?
├─ YES → Put in util file inside module
└─ NO  → Implement BaseExtractor/BaseExporter

Does it depend on another extractor/exporter?
├─ YES → Design has coupling problem - refactor
└─ NO  → Good - keeps modules independent
```

### "What should I import?"

```
In extractors/color/extractor.py:
✅ from copy_that.domain.tokens import Token, TokenType, BaseExtractor
✅ from .utils import helper_function
❌ from copy_that.extractors.spacing import SpacingExtractor

In services/token_service.py:
✅ from copy_that.extractors import get_extractor
✅ from copy_that.domain.tokens import TokenGraph
❌ from copy_that.extractors.color import ColorExtractor

In interfaces/api/tokens_router.py:
✅ from copy_that.services.token_service import TokenService
❌ from copy_that.extractors.color import ColorExtractor
❌ Direct business logic
```

---

## Common Tasks

### Task: Add a new token type (e.g., Border)

**Step 1: Create extractor module**
```python
# src/copy_that/extractors/border/__init__.py
from copy_that.extractors.base import BaseExtractor
from copy_that.domain.tokens import Token, TokenType

class BorderExtractor(BaseExtractor):
    token_type = "border"

    async def extract(self, image_base64: str) -> list[Token]:
        # Your extraction logic
        return [Token(...), Token(...)]
```

**Step 2: Register it**
```python
# src/copy_that/extractors/__init__.py - add one line:
EXTRACTORS["border"] = BorderExtractor
```

**Step 3: Done!** API endpoints work, exports work, everything works.

### Task: Add a new export format (e.g., iOS)

**Step 1: Create exporter module**
```python
# src/copy_that/exporters/ios/__init__.py
from copy_that.exporters.base import BaseExporter
from copy_that.domain.tokens import TokenGraph

class iOSExporter(BaseExporter):
    format_name = "ios"

    async def export(self, token_graph: TokenGraph) -> str:
        # Generate iOS-specific format
        return ios_code
```

**Step 2: Register it**
```python
# src/copy_that/exporters/__init__.py - add one line:
EXPORTERS["ios"] = iOSExporter
```

**Step 3: Done!** API endpoints work, existing features unchanged.

### Task: Add a relationship between tokens

```python
# In your service/extractor logic:
from copy_that.domain.tokens import TokenGraph, RelationType

graph.add_relation(
    source_id="color/01",
    relation_type=RelationType.ALIAS_OF,
    target_id="color/primary",
    metadata={"confidence": 0.95}
)
```

### Task: Resolve a token alias

```python
# In exporter or display logic:
primary_token = graph.resolve_alias("color/primary")
# Follows: color/primary → ALIAS_OF → color/01
# Returns the actual color/01 token
```

---

## Anti-Patterns (What NOT to Do)

| Don't | Do | Why |
|-------|----|----|
| Import ColorExtractor directly | Use get_extractor("color") | Keeps modules independent |
| Create ColorToken, SpacingToken classes | Use Token + TokenType enum | Single representation |
| Store relationships in database only | Use TokenGraph in memory | Relationships are first-class |
| Hardcode extractor in service | Use registry | Easy to swap implementations |
| Let API call extractor directly | Go through service | Proper separation of concerns |
| Cross-module imports | Use interfaces/registries | Zero coupling |

---

## Code Structure Checklist

Before committing code:

- [ ] Is this in the right layer? (domain/extractors/exporters/services/api)
- [ ] Does it import only from domain + base classes + own module?
- [ ] If new extractor/exporter, is it registered?
- [ ] Does it return/consume Token (not TokenType-specific class)?
- [ ] Can it be removed without breaking other modules?
- [ ] Are there tests?
- [ ] Does it follow the patterns in ARCHITECTURE_CONSOLIDATION.md?

---

## Debugging Coupling Problems

**Symptom:** "I need to modify ColorExtractor but I'm worried about breaking other things"

**Diagnosis:** You're tightly coupled. Check for:
- Cross-module imports (extractors/color importing extractors/spacing)
- Hardcoded type checks (if token_type == "color" then use ColorExtractor)
- Direct instantiation instead of registry

**Fix:**
1. Remove the cross-module import
2. Use registry (get_extractor) instead of direct import
3. Use generic Token instead of ColorToken

---

## File Organization Reference

```
src/copy_that/

domain/                              ← STABLE, imported by everything
├── tokens/
│   ├── token.py                    (Token data class)
│   ├── graph.py                    (TokenGraph - the hub)
│   ├── repository.py               (TokenRepository interface)
│   ├── relations.py                (TokenRelation, RelationType)
│   └── __init__.py                 (exports all public interfaces)

extractors/                          ← PLUGIN LAYER (zero coupling)
├── base.py                         (BaseExtractor)
├── color/
│   ├── extractor.py
│   └── utils.py
├── spacing/
│   └── extractor.py
├── typography/
│   └── extractor.py
├── shadow/
│   └── extractor.py
└── __init__.py                     (registry only)

exporters/                           ← PLUGIN LAYER (zero coupling)
├── base.py                         (BaseExporter)
├── w3c/
│   └── exporter.py
├── tailwind/
│   └── exporter.py
├── css/
│   └── exporter.py
└── __init__.py                     (registry only)

services/                            ← ORCHESTRATION (uses registries)
├── token_service.py                (core service)
├── extraction_service.py           (extraction orchestration)
└── export_service.py               (export orchestration)

infrastructure/                      ← SHARED UTILITIES
├── database.py
└── cache.py

interfaces/api/                      ← HTTP TRANSLATION ONLY
├── tokens_router.py
└── schemas.py
```

---

## When to Break This Architecture

**You shouldn't.** But if you must:

1. **Discuss first** - check ARCHITECTURE_CONSOLIDATION.md
2. **Document why** - add comment explaining the violation
3. **Create issue** - track the technical debt
4. **Plan refactor** - schedule time to fix it

Example: If you need to share algorithm between two extractors:
- ❌ DON'T: Import ColorExtractor in SpacingExtractor
- ✅ DO: Move algorithm to shared utility in extractors/utils.py
- ✅ DO: Both extractors import the utility (internal to extractors module)

---

## Testing Each Layer

### Domain Layer
```python
# Test Token, TokenGraph, TokenRepository in isolation
# No dependencies on extractors, services, or API
def test_token_graph_resolves_aliases():
    graph = TokenGraph(...)
    assert graph.resolve_alias("primary") == ...
```

### Extractors
```python
# Test each extractor independently
# Use mock image data, no database needed
@pytest.mark.asyncio
async def test_color_extractor_returns_tokens():
    extractor = ColorExtractor()
    tokens = await extractor.extract(base64_image)
    assert len(tokens) > 0
    assert all(isinstance(t, Token) for t in tokens)
```

### Services
```python
# Test orchestration, not business logic
# Mock extractors/exporters
@pytest.mark.asyncio
async def test_token_service_extracts_and_stores():
    service = TokenService(mock_repository)
    tokens = await service.extract("color", image)
    assert all(t in service.graph for t in tokens)
```

### API
```python
# Test HTTP translation only
# Mock services
def test_extract_endpoint_calls_service():
    client = TestClient(app)
    response = client.post("/api/v1/extract/color", json={...})
    assert response.status_code == 200
```

---

## Performance Considerations

### TokenGraph In-Memory vs Persisted

**In-Memory (Fast, Volatile):**
```python
from copy_that.domain.tokens import TokenRepository, TokenGraph

repository = TokenRepository()  # All in memory
graph = TokenGraph(repository)

# Fast lookups, perfect for single extraction session
```

**Persisted (Slow, Permanent):**
```python
from copy_that.infrastructure.persistence import PersistentTokenRepository

repository = PersistentTokenRepository(db_session)
graph = TokenGraph(repository)

# Slower but survives shutdown
```

Choose based on your use case. Can be swapped - **that's why we abstract it!**

---

## Migration Checklist (From Old to New)

- [ ] Domain layer created + tested
- [ ] Extractors refactored to modules + registered
- [ ] Exporters refactored to modules + registered
- [ ] Services built using registries
- [ ] API routes use services
- [ ] Old code can be removed
- [ ] Tests passing
- [ ] All coupling violations fixed
- [ ] Code review completed
- [ ] Deployed to production

---

This reference should answer 90% of your architecture questions. For detailed info, see ARCHITECTURE_CONSOLIDATION.md.
