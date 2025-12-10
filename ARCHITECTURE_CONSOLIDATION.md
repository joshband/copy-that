# Copy That - Authoritative Architecture Consolidation

**Date:** 2025-12-10
**Status:** AUTHORITATIVE - This document resolves all architecture confusion and defines the standard going forward
**Owner:** Architecture Council

---

## Executive Summary

Your architecture is currently **split between two realities**:

1. **Vision Docs** (excellent): Describe a modular, zero-coupling token platform with TokenGraph at the center
2. **Actual Code**: Still using legacy pipeline structure without true modularity

**This document reconciles both and provides the authoritative path forward.**

---

## Question 1: Are We Using a Graph Data Structure?

### ✅ YES - TokenGraph IS the Central Model

TokenGraph is **not optional** - it's the fundamental architectural choice that enables everything else:

```python
# This is the core data structure
class Token:
    id: str                      # "color/primary", "spacing/xs"
    type: TokenType              # COLOR, SPACING, TYPOGRAPHY, SHADOW, etc.
    value: Any                   # "#FF5733", 16, "Inter 16px", etc.
    attributes: dict             # metadata: confidence, harmony, harmony_score, etc.
    relations: list[TokenRelation]  # ALIAS_OF, MULTIPLE_OF, REFERENCES

class TokenRelation:
    source_id: str              # "color/primary"
    relation_type: RelationType # ALIAS_OF, MULTIPLE_OF, REFERENCES, DERIVED_FROM
    target_id: str              # "color/00"
    metadata: dict              # multiplier: 2, reasoning: "90% of primary", etc.

class TokenGraph:
    """Central intelligent hub managing all token relationships"""
    repository: TokenRepository  # In-memory or persisted store

    # Core operations
    add_token(token: Token) -> Token
    get_token(token_id: str) -> Token | None
    add_relation(source_id, relation_type, target_id, metadata) -> None

    # Graph intelligence
    resolve_alias(token_id: str) -> Token          # Follow alias chain
    get_dependents(token_id: str) -> list[Token]   # What depends on this?
    detect_cycles() -> list[list[str]]             # Validate integrity
    validate() -> ValidationResult                 # Full graph validation
```

**Why TokenGraph is essential:**
- ✅ Enables semantic relationships (not just flat lists)
- ✅ Supports W3C design token composition
- ✅ Resolves aliases automatically
- ✅ Detects cycles and invalid references
- ✅ Enables ramp generation (e.g., primary → 100 shades)
- ✅ Supports multi-modal extensions (audio tokens have relationships too)

---

## Current State (Reality Check)

### What EXISTS Today

```
✅ IMPLEMENTED:
- Database models (color_tokens, spacing_tokens, typography_tokens, shadow_tokens)
- Extraction pipelines (application/color, cv, etc.)
- FastAPI endpoints (REST API)
- Token-specific code (tokens/color/, tokens/spacing/)
- Basic services (services/color.py, etc.)

❌ NOT IMPLEMENTED:
- TokenGraph class (the core data structure)
- TokenRepository abstraction
- Modular extractor/exporter plugin system
- Zero-coupling architecture
- Token relationship management
- Unified token representation
```

### What's MISSING

The code is organized by **concern** (extraction, persistence) but NOT by **modularity**:

```
CURRENT (Wrong):
src/copy_that/
├── application/        ← Extraction logic (tightly coupled)
├── tokens/            ← Token-specific code (should be generic)
├── pipeline/          ← Legacy extraction pipeline
├── services/          ← Orchestration (depends on everything)
└── infrastructure/    ← Database, cache

DESIRED (After Refactor):
src/copy_that/
├── domain/                    ← TokenGraph, Token, core abstractions
├── extractors/                ← Modular, independent
│   ├── base.py
│   ├── color/
│   └── spacing/
├── exporters/                 ← Modular, independent
│   ├── base.py
│   ├── w3c/
│   └── tailwind/
├── services/                  ← Orchestration (uses registries)
├── infrastructure/            ← Database, cache
└── interfaces/api/            ← HTTP translation only
```

---

## Authoritative Architecture (NEW)

### Layer 1: Domain (Core Abstractions)

**File:** `src/copy_that/domain/tokens/`

This layer is **STABLE** - all other layers import from here.

```python
# src/copy_that/domain/tokens/__init__.py
# EXPORTS ONLY:
# - Token (data class)
# - TokenType (enum)
# - TokenRelation (data class)
# - TokenRepository (abstract interface)
# - TokenGraph (the central hub)
# - RelationType (enum)
# - TokenValue (type alias)
```

**Key rule:** Domain layer has **zero dependencies** on other layers (except Python stdlib).

### Layer 2: Extractors (Modular, Independent)

**Philosophy:** Each extractor is a completely independent plugin.

```
src/copy_that/extractors/
├── __init__.py                    # REGISTRY ONLY
├── base.py                        # BaseExtractor (abstract)
│
├── color/
│   ├── __init__.py
│   ├── extractor.py              # ColorExtractor(BaseExtractor)
│   ├── kmeans.py                 # Internal algorithm
│   └── utils.py                  # Internal helpers
│
├── spacing/
│   ├── __init__.py
│   ├── extractor.py
│   └── utils.py
│
├── typography/
│   ├── __init__.py
│   ├── extractor.py
│   └── recommender.py
│
└── shadow/
    ├── __init__.py
    └── extractor.py
```

**Coupling Rules:**

```python
# ✅ ALLOWED in extractor/color/extractor.py:
from copy_that.domain.tokens import Token, TokenType, BaseExtractor
from copy_that.extractors.base import BaseExtractor
from .kmeans import KMeansColorExtractor
import logging

# ❌ FORBIDDEN:
from copy_that.extractors.spacing import SpacingExtractor  # Cross-module import
from copy_that.services.extraction_service import *       # Circular dependency
from copy_that.application.color_extractor import *       # Coupling to old code
```

**BaseExtractor Interface:**

```python
from abc import ABC, abstractmethod
from copy_that.domain.tokens import Token

class BaseExtractor(ABC):
    """All extractors implement this interface."""

    token_type: str = "unknown"  # Subclasses override: "color", "spacing", etc.

    @abstractmethod
    async def extract(self, input_data: str | bytes) -> list[Token]:
        """Extract tokens from input.

        Args:
            input_data: Base64 image (for visual extractors) or other input

        Returns:
            List of Token objects with complete attributes
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: str | bytes) -> bool:
        """Validate that input is in correct format."""
        pass

    async def preprocess(self, input_data: str | bytes) -> str | bytes:
        """Optional preprocessing."""
        return input_data

    async def postprocess(self, tokens: list[Token]) -> list[Token]:
        """Optional postprocessing."""
        return tokens
```

**Registry Pattern (Zero Coupling):**

```python
# src/copy_that/extractors/__init__.py
from typing import Type, Dict, Optional
from copy_that.extractors.base import BaseExtractor
from copy_that.extractors.color import ColorExtractor
from copy_that.extractors.spacing import SpacingExtractor
from copy_that.extractors.typography import TypographyExtractor
from copy_that.extractors.shadow import ShadowExtractor

# Registry: single place where modules are declared
EXTRACTORS: Dict[str, Type[BaseExtractor]] = {
    "color": ColorExtractor,
    "spacing": SpacingExtractor,
    "typography": TypographyExtractor,
    "shadow": ShadowExtractor,
}

def get_extractor(token_type: str) -> BaseExtractor:
    """Factory function - services use this, NOT direct imports."""
    if token_type not in EXTRACTORS:
        raise ValueError(f"Unknown extractor: {token_type}")
    return EXTRACTORS[token_type]()
```

**Services use registry, never direct imports:**

```python
# ✅ CORRECT in services/extraction_service.py:
from copy_that.extractors import get_extractor
from copy_that.domain.tokens import Token, TokenGraph

async def extract_tokens(token_type: str, image_base64: str) -> list[Token]:
    extractor = get_extractor(token_type)  # Get via registry
    tokens = await extractor.extract(image_base64)
    return tokens

# ❌ WRONG (don't do this):
from copy_that.extractors.color import ColorExtractor  # Direct import = coupling
```

### Layer 3: Exporters (Modular, Independent)

**Same pattern as extractors, but different responsibility:**

```
src/copy_that/exporters/
├── __init__.py                    # REGISTRY ONLY
├── base.py                        # BaseExporter (abstract)
│
├── w3c/
│   ├── __init__.py
│   ├── exporter.py               # W3CExporter(BaseExporter)
│   └── utils.py
│
├── tailwind/
│   ├── __init__.py
│   └── exporter.py
│
├── css/
│   ├── __init__.py
│   └── exporter.py
│
└── figma/
    ├── __init__.py
    └── exporter.py
```

**BaseExporter Interface:**

```python
from abc import ABC, abstractmethod
from copy_that.domain.tokens import TokenGraph

class BaseExporter(ABC):
    """All exporters implement this interface."""

    format_name: str = "unknown"  # Subclasses override: "w3c", "tailwind", etc.

    @abstractmethod
    async def export(self, token_graph: TokenGraph) -> dict | str:
        """Export token graph to format.

        Args:
            token_graph: The TokenGraph containing all tokens and relationships

        Returns:
            Exported data (dict for JSON-like, str for CSS/text)
        """
        pass

    @abstractmethod
    def validate_graph(self, token_graph: TokenGraph) -> bool:
        """Validate that graph is exportable in this format."""
        pass
```

### Layer 4: Services (Orchestration)

**Services orchestrate extractors and exporters - they know about registries, NOT implementations:**

```python
# src/copy_that/services/token_service.py
from copy_that.extractors import get_extractor
from copy_that.exporters import get_exporter
from copy_that.domain.tokens import TokenGraph, TokenRepository

class TokenService:
    """Core service - orchestrates extraction and export."""

    def __init__(self, repository: TokenRepository):
        self.repository = repository
        self.graph = TokenGraph(repository)

    async def extract(self, token_type: str, image_base64: str) -> list[Token]:
        """Extract tokens - uses registry, not direct imports."""
        extractor = get_extractor(token_type)  # ✅ Via registry
        tokens = await extractor.extract(image_base64)

        # Add to graph
        for token in tokens:
            self.repository.add_token(token)

        return tokens

    async def export(self, format_type: str) -> dict | str:
        """Export tokens - uses registry, not direct imports."""
        exporter = get_exporter(format_type)  # ✅ Via registry
        result = await exporter.export(self.graph)
        return result
```

### Layer 5: API (HTTP Translation)

**API endpoints are PURE translation - they call services, nothing else:**

```python
# src/copy_that/interfaces/api/tokens_router.py
from fastapi import APIRouter
from copy_that.services.token_service import TokenService
from copy_that.domain.tokens import TokenGraph

router = APIRouter(prefix="/api/v1")

@router.post("/extract/{token_type}")
async def extract_tokens(token_type: str, request: ExtractRequest, service: TokenService):
    """Extract tokens of specified type."""
    tokens = await service.extract(token_type, request.image_base64)
    return {"tokens": tokens}

@router.post("/export/{format_type}")
async def export_tokens(format_type: str, service: TokenService):
    """Export tokens to specified format."""
    result = await service.export(format_type)
    return result
```

---

## Understanding TokenGraph In Practice

### Example 1: Color Extraction → Graph → Export

```python
# Step 1: Extract colors from image
async def extract_colors(image_base64: str):
    extractor = get_extractor("color")
    raw_tokens = await extractor.extract(image_base64)
    # Returns: [
    #   Token(id="color/00", type=COLOR, value="#FF5733", attributes={...}),
    #   Token(id="color/01", type=COLOR, value="#3498DB", attributes={...}),
    # ]

# Step 2: Add to graph
repository = TokenRepository()
graph = TokenGraph(repository)

for token in raw_tokens:
    repository.add_token(token)

# Step 3: Add relationships (e.g., if color/01 is actually primary blue)
graph.add_relation(
    source_id="color/01",
    relation_type=RelationType.ALIAS_OF,
    target_id="color/primary",
    metadata={"confidence": 0.95, "semantic": "primary_blue"}
)

# Step 4: Export to W3C format (graph contains all relationships)
exporter = get_exporter("w3c")
w3c_tokens = await exporter.export(graph)
# Exporter sees:
# - All tokens (color/00, color/01, color/primary, etc.)
# - All relationships (color/01 ALIAS_OF color/primary)
# - Can generate proper token references
```

### Example 2: Color Ramps (Composition via Graph)

```python
# Given primary color, generate ramps (lighter/darker shades)
primary_token = graph.get_token("color/primary")

# Create ramp tokens (lighter versions)
for i in range(1, 6):
    lightness = 90 - (i * 10)  # 80%, 70%, 60%, 50%, 40%
    ramp_token = Token(
        id=f"color/primary-light-{i:02d}",
        type=TokenType.COLOR,
        value=lighten(primary_token.value, lightness),
        attributes={"lightness": lightness, "base": "primary"}
    )
    repository.add_token(ramp_token)

    # Create relationship
    graph.add_relation(
        source_id=ramp_token.id,
        relation_type=RelationType.DERIVED_FROM,
        target_id="color/primary",
        metadata={"operation": "lighten", "value": lightness}
    )

# Now when exporting, the ramps are properly attributed to primary
```

---

## Migration Path: From Current → Desired State

### Phase 1: Build Domain Layer (Week 1)

✅ This is **non-breaking** - build alongside existing code

```
1. Create src/copy_that/domain/tokens/
   - token.py (Token, TokenType, TokenValue data classes)
   - graph.py (TokenGraph class)
   - repository.py (TokenRepository abstract interface)
   - relations.py (TokenRelation, RelationType enums)
   - __init__.py (exports all public interfaces)

2. NO dependencies on existing code
3. Full test coverage
4. Can exist alongside current code without conflicts
```

### Phase 2: Build Extractor Plugins (Week 2-3)

✅ Non-breaking - new code path

```
1. Create src/copy_that/extractors/
   - base.py (BaseExtractor abstract class)
   - color/ (ColorExtractor implementation)
   - spacing/ (SpacingExtractor implementation)
   - typography/ (TypographyExtractor implementation)
   - shadow/ (ShadowExtractor implementation)
   - __init__.py (registry)

2. Extractors return Token objects (use new domain layer)
3. Keep old pipeline code temporarily
4. Create new extraction_v2 service using new extractors
```

### Phase 3: Build Exporter Plugins (Week 3-4)

✅ Non-breaking - new code path

```
1. Create src/copy_that/exporters/
   - base.py (BaseExporter abstract class)
   - w3c/ (W3CExporter)
   - tailwind/ (TailwindExporter)
   - css/ (CSSExporter)
   - __init__.py (registry)

2. Exporters consume TokenGraph
3. Create new export_v2 service using new exporters
4. Keep old exporters temporarily
```

### Phase 4: Build New Services (Week 4)

✅ Non-breaking - uses new layers

```
1. Create src/copy_that/services/token_service.py
   - Uses registries (get_extractor, get_exporter)
   - Orchestrates extraction and export
   - Manages TokenGraph
   - NO direct imports of extractors/exporters

2. Full test coverage
3. Runs alongside old services
```

### Phase 5: Build New API Endpoints (Week 5)

✅ Non-breaking - new routes

```
1. Create src/copy_that/interfaces/api/v2/
   - tokens_router.py (new endpoints)
   - Uses TokenService

2. Old API routes unchanged
3. Both versions available during transition
```

### Phase 6: Migrate, Test, Deploy (Week 5-6)

✅ Controlled migration

```
1. Redirect API routes to new service
2. Run both code paths initially (validation)
3. Remove old code (application/, old services/)
4. Commit the refactor
```

---

## Concrete Example: Adding Audio Tokens (Future)

This shows why zero-coupling with TokenGraph matters:

### Current Approach (Tightly Coupled)

If we wanted to add audio tokens TODAY, we'd need to:
1. Create `application/audio_extractor.py` (tied to application/)
2. Create `audio_tokens` table
3. Modify services (add audio logic)
4. Modify API routes (add audio endpoints)
5. Modify UI (add audio widgets)
**= 50+ files touched, high risk of breaking things**

### New Approach (Zero-Coupling)

With the modular architecture:

```python
# Step 1: Create new extractor module (completely independent)
# src/copy_that/extractors/audio/__init__.py
from copy_that.extractors.base import BaseExtractor
from copy_that.domain.tokens import Token, TokenType

class AudioExtractor(BaseExtractor):
    token_type = "audio"

    async def extract(self, audio_base64: str) -> list[Token]:
        # Audio extraction logic (pitch, timbre, rhythm, etc.)
        # Returns Token objects (same as color, spacing)
        pass

# Step 2: Register it (one line)
# src/copy_that/extractors/__init__.py
EXTRACTORS = {
    "color": ColorExtractor,
    "spacing": SpacingExtractor,
    "audio": AudioExtractor,  # ← Add this
}

# Step 3: DONE - everything else works automatically
# - API endpoints work (same generic endpoints)
# - Export works (TokenGraph handles any token type)
# - Services work (use registries, not hardcoded types)
# - Frontend works (same UI for any token type)
```

**That's it.** No modifying existing extractors, services, API routes, or UI components. **True modularity.**

---

## Token Representation: Visual Tokens as Reference

To ground this in reality, here's how Visual Tokens work WITH TokenGraph:

### Visual Token Adapter Example

```python
# src/copy_that/adapters/visual_adapter.py
# This CONSUMES TokenGraph, doesn't dictate it

from copy_that.domain.tokens import Token, TokenGraph

class VisualTokenAdapter:
    """Adapt generic Token objects for visual display."""

    def to_ui_format(self, token: Token) -> dict:
        """Convert Token → UI-friendly representation."""

        if token.type == TokenType.COLOR:
            return {
                "id": token.id,
                "value": token.value,
                "hex": token.value,
                "rgb": token.attributes.get("rgb"),
                "harmony": token.attributes.get("harmony"),
                "confidence": token.attributes.get("confidence"),
                # ... other color-specific fields
            }

        elif token.type == TokenType.SPACING:
            return {
                "id": token.id,
                "value": token.value,
                "px": token.value,
                "semantic_role": token.attributes.get("semantic_role"),
                # ... other spacing fields
            }

        # etc. for typography, shadow, audio, etc.
        # ALL use same Token interface
```

The key insight: **Adapters transform generic Tokens for specific needs, but never modify the core Token/TokenGraph architecture.**

---

## Architecture Validation Rules (Test These)

### Rule 1: No Cross-Module Imports

```python
# ✅ GOOD:
from copy_that.extractors.base import BaseExtractor
from copy_that.domain.tokens import Token

# ❌ BAD (violates zero-coupling):
from copy_that.extractors.color import ColorExtractor
from copy_that.extractors.spacing import SpacingExtractor
```

### Rule 2: Services Use Registries

```python
# ✅ GOOD:
extractor = get_extractor("color")

# ❌ BAD:
from copy_that.extractors.color import ColorExtractor
extractor = ColorExtractor()
```

### Rule 3: API Uses Services Only

```python
# ✅ GOOD:
async def extract_colors(service: TokenService):
    return await service.extract("color", image_base64)

# ❌ BAD:
async def extract_colors(image_base64: str):
    extractor = ColorExtractor()
    return await extractor.extract(image_base64)
```

### Rule 4: Domain Layer Has Zero Dependencies

```python
# ✅ GOOD in domain/:
from typing import Optional, List, Dict
import dataclasses
from enum import Enum

# ❌ BAD in domain/:
from copy_that.services import SomeService
import external_library
```

---

## Visual Diagram: Data Flow With TokenGraph

```
┌─────────────────────────────────────────────────────────────┐
│ API Endpoint: POST /api/v1/extract/color                   │
├─────────────────────────────────────────────────────────────┤
│ Input: { "image_base64": "..." }                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ TokenService.extract(token_type="color", image_base64)      │
├─────────────────────────────────────────────────────────────┤
│ 1. extractor = get_extractor("color")  [Registry]          │
│ 2. tokens = await extractor.extract(image_base64)           │
│ 3. for token in tokens:                                     │
│    repository.add_token(token)         [Add to graph]       │
│ 4. return tokens                                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ ColorExtractor.extract(image_base64)                        │
├─────────────────────────────────────────────────────────────┤
│ 1. raw_colors = kmeans_extract(image_base64)               │
│ 2. for color in raw_colors:                                │
│    token = Token(                                          │
│      id=f"color/{i:02d}",                                  │
│      type=TokenType.COLOR,                                 │
│      value=color.hex,                                      │
│      attributes={...}                                      │
│    )                                                       │
│ 3. return tokens  [List[Token]]                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ TokenGraph (Central Hub)                                    │
├─────────────────────────────────────────────────────────────┤
│ repository: {                                              │
│   "color/00": Token(...),                                  │
│   "color/01": Token(...),                                  │
│   "color/primary": Token(ALIAS_OF → color/01),            │
│   ...                                                      │
│ }                                                          │
│                                                            │
│ relations: [                                               │
│   Relation(color/primary ALIAS_OF color/01),              │
│   ...                                                      │
│ ]                                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓ (When exporting)
┌─────────────────────────────────────────────────────────────┐
│ W3CExporter.export(graph)                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. For each token in graph:                               │
│    - Resolve aliases                                       │
│    - Follow relationships                                  │
│    - Generate W3C JSON                                     │
│ 2. return {                                                │
│      "$schema": "...",                                     │
│      "color": {                                            │
│        "primary": {"$value": "..." },                      │
│        "00": {"$value": "..." }                            │
│      }                                                     │
│    }                                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary: What's Different

| Aspect | Current (Legacy) | New (Modular) |
|--------|------------------|---------------|
| **Coupling** | Tight (extractors import extractors) | Zero (via registries) |
| **Token Representation** | Scattered (ColorToken, SpacingToken, etc.) | Unified (Token + TokenType enum) |
| **Relationships** | Not supported | First-class in TokenGraph |
| **Adding New Type** | Modify 20+ files | Create 1 module, add to registry |
| **Exporting** | Hardcoded per type | Generic (TokenGraph → any format) |
| **Testing** | Coupled, brittle | Independent modules, robust |
| **Future Extensibility** | Low (would need full refactor) | High (just add module + register) |

---

## Next Steps

### Immediate (Today)
1. ✅ Read this document (you're doing it!)
2. Review the GOALS with this understanding
3. Decide: implement this architecture now or keep legacy code

### If Implementing (Week 1-6)
1. Create domain layer (Phase 1) - non-breaking
2. Refactor extractors into modules (Phase 2)
3. Refactor exporters into modules (Phase 3)
4. Build new services (Phase 4)
5. Build new API (Phase 5)
6. Migrate and clean up (Phase 6)

### Architecture Review Checklist

Use this when reviewing ANY code change:

```
□ Does this module import from another module's implementation?
  - If YES, it violates zero-coupling
□ Does a service hardcode which extractor/exporter to use?
  - If YES, it should use a registry
□ Does a token class exist that isn't in domain/tokens/?
  - If YES, it should be a Token + TokenType instead
□ Can this module be replaced without changing others?
  - If NO, it's too tightly coupled
□ Does the API endpoint call domain logic directly?
  - If YES, it should go through a service
```

---

## Questions This Answers

**Q: Are we using a graph data structure?**
A: YES, TokenGraph is THE central architecture. It's designed but not yet implemented in code.

**Q: Why does the code feel messy?**
A: The vision docs describe the right architecture, but the code hasn't been refactored to match. This is the plan to fix that.

**Q: Do we really need zero-coupling?**
A: YES. Without it, adding audio tokens, or any new feature, requires touching dozens of files. With it, you add 1 module.

**Q: What about the current extractors?**
A: They need to be reorganized into independent modules that return Token objects instead of token-specific types.

**Q: How do we migrate without breaking?**
A: Phase approach - build new alongside old, switch when ready, delete old.

**Q: Is TokenGraph just for colors?**
A: NO. TokenGraph handles ANY token type (color, spacing, typography, audio, video, text, etc.) because tokens are generic.

---

**This is your single source of truth for architecture going forward. All future decisions should reference this document.**
