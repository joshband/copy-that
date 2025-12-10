# Modular Zero-Coupling Architecture

**Principle:** No module imports another module's implementation. Only base interfaces, registries, and domain models.

**Result:** Each module is completely independent, testable, replaceable, and extensible.

---

## Architecture Layers (Zero-Coupling Boundaries)

```
┌─────────────────────────────────────────┐
│         API Layer (HTTP Translation)    │
│         ← Just calls services via       │
│           dependency injection          │
└─────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────┐
│         Service Layer                   │
│         ← Uses registries to get        │
│           implementations               │
└─────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────┐
│    Registry/Factory Layer                │
│    ← Single place modules are registered│
└─────────────────────────────────────────┘
                    ↑
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
┌──────────┐   ┌──────────┐   ┌──────────┐
│Extractor │   │Extractor │   │Extractor │
│ Module 1 │   │ Module 2 │   │ Module 3 │
│(COLOR)   │   │(SPACING) │   │(TYPO)    │
│ ↓ imports:    │ ↓ imports:    │ ↓ imports:
│ - base.py    │ - base.py    │ - base.py
│ - Token      │ - Token      │ - Token
│ - nothing    │ - nothing    │ - nothing
│  else        │  else        │  else
└──────────┘   └──────────┘   └──────────┘

    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Exporter │   │ Exporter │   │ Exporter │
│(W3C)     │   │(TAILWIND)│   │(CSS)     │
│ ↓ imports:    │ ↓ imports:    │ ↓ imports:
│ - base.py    │ - base.py    │ - base.py
│ - Token      │ - Token      │ - Token
│ - Graph      │ - Graph      │ - Graph
│ - nothing    │ - nothing    │ - nothing
│  else        │  else        │  else
└──────────┘   └──────────┘   └──────────┘
                    ↑
┌─────────────────────────────────────────┐
│    Domain Layer (Stable Abstractions)    │
│    - Token                              │
│    - TokenRepository                    │
│    - TokenGraph                         │
│    - TokenType enum                     │
│    - TokenRelation                      │
│                                         │
│    ← All modules import from here       │
│    ← No business logic here             │
│    ← Pure data structures               │
└─────────────────────────────────────────┘
```

---

## Coupling Rules (Strict)

### ✅ ALLOWED

```python
# In any module (color, spacing, exporter, etc.):
from copy_that.domain.tokens import Token, TokenType, TokenRepository, TokenGraph
from copy_that.extractors.base import BaseExtractor
from copy_that.exporters.base import BaseExporter
from typing import List, Optional
import logging
```

### ❌ FORBIDDEN

```python
# NEVER do this in any module:
from copy_that.extractors.color import ColorKMeansExtractor  # NO - cross-module import
from copy_that.exporters.w3c_exporter import W3CExporter     # NO - cross-module import
from copy_that.services.extraction_service import *         # NO - circular dependency
from copy_that.interfaces.api import router                 # NO - API imports implementation
```

---

## File Structure (With Coupling Boundaries)

```
src/copy_that/

├── domain/                                  🔒 STABLE LAYER
│   ├── __init__.py
│   ├── tokens/
│   │   ├── __init__.py
│   │   │   # ✅ Safe to import: Token, TokenType, TokenRepository, TokenGraph
│   │   ├── token.py                        # Data structure only
│   │   ├── repository.py                   # Abstract interface only
│   │   └── graph.py                        # Graph abstraction only
│   │
│   ├── enums.py                            # TokenType, RelationType, TokenValueType
│   └── exceptions.py                       # Custom exceptions
│
├── extractors/                              🔌 PLUGIN LAYER (ZERO COUPLING)
│   ├── __init__.py                         # Registry ONLY - declares what exists
│   ├── base.py                             # BaseExtractor abstract class
│   │
│   ├── color/                              # 🧪 INDEPENDENT MODULE
│   │   ├── __init__.py                     # Module public interface
│   │   ├── extractor.py                    # ColorExtractor class
│   │   │   ✅ Imports: Token, TokenType, BaseExtractor
│   │   │   ❌ Does NOT import: spacing, typography, any other extractor
│   │   ├── kmeans.py                       # K-means algorithm (module-internal)
│   │   ├── strategies.py                   # Strategy pattern (module-internal)
│   │   └── utils.py                        # Helper functions (module-internal)
│   │
│   ├── spacing/                            # 🧪 INDEPENDENT MODULE
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   │   ✅ Imports: Token, TokenType, BaseExtractor
│   │   │   ❌ Does NOT import: color, typography
│   │   └── utils.py
│   │
│   ├── typography/                         # 🧪 INDEPENDENT MODULE
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   │   ✅ Imports: Token, TokenType, BaseExtractor
│   │   │   ❌ Does NOT import: color, spacing
│   │   └── recommender.py
│   │
│   └── shadow/                             # 🧪 INDEPENDENT MODULE
│       ├── __init__.py
│       └── extractor.py
│           ✅ Imports: Token, TokenType, BaseExtractor
│           ❌ Does NOT import: color, spacing, typography
│
├── exporters/                              🔌 PLUGIN LAYER (ZERO COUPLING)
│   ├── __init__.py                        # Registry ONLY
│   ├── base.py                            # BaseExporter abstract class
│   │
│   ├── w3c/                               # 🧪 INDEPENDENT MODULE
│   │   ├── __init__.py
│   │   ├── exporter.py
│   │   │   ✅ Imports: Token, TokenGraph, BaseExporter
│   │   │   ❌ Does NOT import: tailwind, css, figma exporters
│   │   └── utils.py
│   │
│   ├── tailwind/                          # 🧪 INDEPENDENT MODULE
│   │   ├── __init__.py
│   │   └── exporter.py
│   │       ✅ Imports: Token, TokenGraph, BaseExporter
│   │       ❌ Does NOT import: w3c, css, figma
│   │
│   ├── css/                               # 🧪 INDEPENDENT MODULE
│   │   ├── __init__.py
│   │   └── exporter.py
│   │
│   └── figma/                             # 🧪 INDEPENDENT MODULE
│       ├── __init__.py
│       └── exporter.py
│
├── services/                              ⚙️ ORCHESTRATION LAYER
│   ├── __init__.py
│   ├── extraction_service.py              # Uses extractors via registry
│   │   ✅ Imports: BaseExtractor, TokenRepository, TokenGraph
│   │   ✅ Uses: get_extractor() from extractors.__init__
│   │   ❌ Direct imports of ColorExtractor, SpacingExtractor, etc.
│   │
│   ├── export_service.py                  # Uses exporters via registry
│   │   ✅ Imports: BaseExporter, TokenGraph
│   │   ✅ Uses: get_exporter() from exporters.__init__
│   │   ❌ Direct imports of W3CExporter, TailwindExporter, etc.
│   │
│   └── curation_service.py                # Graph manipulation
│       ✅ Imports: Token, TokenGraph, TokenRepository
│
├── infrastructure/                        📦 SHARED UTILITIES
│   ├── __init__.py
│   ├── persistence/
│   │   └── database.py                    # Database session (shared)
│   └── cache.py                           # Caching (shared)
│
└── interfaces/api/                        🌐 HTTP TRANSLATION LAYER
    ├── __init__.py
    ├── tokens_router.py                   # Generic token endpoints
    │   ✅ Imports: ExtractionService, ExportService
    │   ✅ Uses: dependency injection
    │   ❌ Does NOT import any extractor or exporter
    │
    ├── schemas.py                         # Pydantic models (request/response)
    ├── dependencies.py                    # FastAPI dependencies
    └── middleware/
        └── error_handling.py              # Error handling (shared)
```

---

## Implementation Pattern: Registry Without Coupling

### Step 1: Base Interface (Stable)

```python
# src/copy_that/extractors/base.py
# ✅ CAN be imported by all extractor modules

from abc import ABC, abstractmethod
from typing import Sequence
from copy_that.domain.tokens import Token

class BaseExtractor(ABC):
    """All extractors implement this."""

    token_type: str  # Subclasses define: "color", "spacing", etc.

    @abstractmethod
    async def extract(self, image_base64: str) -> Sequence[Token]:
        """Extract tokens from image."""
        pass
```

### Step 2: Implementations (Independent)

```python
# src/copy_that/extractors/color/__init__.py
# ✅ ONLY imports: base.py, Token, domain model, internal utils
# ❌ Does NOT import: spacing, typography, or other extractors

from copy_that.extractors.base import BaseExtractor
from copy_that.domain.tokens import Token, TokenType

class ColorExtractor(BaseExtractor):
    token_type = "color"

    async def extract(self, image_base64: str) -> list[Token]:
        # Color extraction logic (K-means, etc.)
        pass

# src/copy_that/extractors/spacing/__init__.py
# ✅ ONLY imports: base.py, Token, domain model, internal utils
# ❌ Does NOT import: color, typography, or other extractors

class SpacingExtractor(BaseExtractor):
    token_type = "spacing"

    async def extract(self, image_base64: str) -> list[Token]:
        # Spacing extraction logic
        pass
```

### Step 3: Registry (Single Point of Registration)

```python
# src/copy_that/extractors/__init__.py
# ✅ This is the ONLY place where implementations are imported
# ✅ Creates factory functions
# ❌ Modules DO NOT import from here

from typing import Type, Dict
from copy_that.extractors.base import BaseExtractor

# Import implementations (ONLY in this file)
from copy_that.extractors.color import ColorExtractor
from copy_that.extractors.spacing import SpacingExtractor
from copy_that.extractors.typography import TypographyExtractor
from copy_that.extractors.shadow import ShadowExtractor

# Registry: maps IDs to classes
_EXTRACTOR_REGISTRY: Dict[str, Type[BaseExtractor]] = {
    "color": ColorExtractor,
    "spacing": SpacingExtractor,
    "typography": TypographyExtractor,
    "shadow": ShadowExtractor,
}

def get_extractor(extractor_id: str) -> BaseExtractor:
    """Factory: get extractor by ID without importing its module."""
    if extractor_id not in _EXTRACTOR_REGISTRY:
        raise ValueError(f"Unknown extractor: {extractor_id}")
    return _EXTRACTOR_REGISTRY[extractor_id]()

def list_available_extractors() -> list[str]:
    """List all registered extractors."""
    return list(_EXTRACTOR_REGISTRY.keys())
```

### Step 4: Service Layer (Uses Registry, NOT Direct Imports)

```python
# src/copy_that/services/extraction_service.py
# ✅ Imports: BaseExtractor, get_extractor function
# ❌ Does NOT import: ColorExtractor, SpacingExtractor directly

from copy_that.extractors import get_extractor  # Factory function, not implementation
from copy_that.domain.tokens import TokenRepository, TokenGraph, Token

class ExtractionService:
    def __init__(self, repo: TokenRepository):
        self.repo = repo

    async def extract_tokens(
        self,
        image_base64: str,
        token_types: list[str] = None
    ) -> TokenGraph:
        """Extract any token types - service doesn't know which extractors exist."""

        if not token_types:
            token_types = ["color", "spacing", "typography"]

        # Use registry to get extractors dynamically
        all_tokens: list[Token] = []
        for token_type in token_types:
            # Get extractor from registry - no direct import needed
            extractor = get_extractor(token_type)

            # Extract tokens
            tokens = await extractor.extract(image_base64)
            all_tokens.extend(tokens)

        # Add to repository
        for token in all_tokens:
            self.repo.add_token(token)

        # Build graph
        graph = TokenGraph(self.repo)
        self._build_relationships(graph, all_tokens)

        return graph

    def _build_relationships(self, graph: TokenGraph, tokens: list[Token]):
        """Build relationships between tokens."""
        # Find colors, generate ramps, add relationships, etc.
        pass
```

### Step 5: API Layer (Pure HTTP Translation)

```python
# src/copy_that/interfaces/api/tokens_router.py
# ✅ Imports: ExtractionService, ExportService (classes, not implementations)
# ❌ Does NOT import: any extractor, any exporter

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from copy_that.services.extraction_service import ExtractionService
from copy_that.services.export_service import ExportService
from copy_that.domain.tokens import TokenRepository

router = APIRouter(prefix="/api/v1", tags=["tokens"])

class ExtractRequest(BaseModel):
    image_base64: str
    token_types: list[str] = ["color", "spacing", "typography"]
    export_formats: list[str] = ["w3c"]

@router.post("/extract")
async def extract_tokens(request: ExtractRequest):
    """Extract tokens - doesn't care which extractors are registered."""

    # Dependency injection
    repo = TokenRepository()
    extraction_service = ExtractionService(repo)
    export_service = ExportService()

    # Extract
    graph = await extraction_service.extract_tokens(
        request.image_base64,
        token_types=request.token_types
    )

    # Export
    exports = await export_service.export(
        graph,
        formats=request.export_formats
    )

    return {
        "tokens": exports,
        "metadata": {
            "extracted_types": request.token_types,
            "formats": request.export_formats
        }
    }
```

---

## Adding New Module Without Touching Existing Code

### Add New Extractor (e.g., "audio")

1. **Create module** (zero coupling to other extractors):
```python
# src/copy_that/extractors/audio/__init__.py
from copy_that.extractors.base import BaseExtractor
from copy_that.domain.tokens import Token, TokenType

class AudioExtractor(BaseExtractor):
    token_type = "audio"

    async def extract(self, audio_base64: str) -> list[Token]:
        # Extract audio tokens
        pass
```

2. **Register in one place only**:
```python
# src/copy_that/extractors/__init__.py
from copy_that.extractors.audio import AudioExtractor

_EXTRACTOR_REGISTRY: Dict[str, Type[BaseExtractor]] = {
    # ... existing ...
    "audio": AudioExtractor,  # ← Add here
}
```

3. **No other files changed** - Services, API, exporters don't know about new extractor

### Add New Exporter (e.g., "swift")

1. **Create module** (zero coupling to other exporters):
```python
# src/copy_that/exporters/swift/__init__.py
from copy_that.exporters.base import BaseExporter
from copy_that.domain.tokens import TokenGraph

class SwiftExporter(BaseExporter):
    format_name = "swift"

    async def export(self, graph: TokenGraph) -> dict:
        # Export as Swift UI format
        pass
```

2. **Register in one place only**:
```python
# src/copy_that/exporters/__init__.py
from copy_that.exporters.swift import SwiftExporter

_EXPORTER_REGISTRY: Dict[str, Type[BaseExporter]] = {
    # ... existing ...
    "swift": SwiftExporter,  # ← Add here
}
```

3. **No other files changed** - API, services, other exporters don't know about new exporter

---

## Testing (Enabled by Zero Coupling)

### Test Color Extractor (In Isolation)

```python
# tests/extractors/test_color_extractor.py
# ✅ Can test without any other extractor
# ✅ No need to import/instantiate other extractors

import pytest
from copy_that.extractors.color import ColorExtractor
from copy_that.domain.tokens import TokenType

@pytest.mark.asyncio
async def test_color_extraction():
    extractor = ColorExtractor()
    tokens = await extractor.extract("base64_image_here")

    assert len(tokens) > 0
    assert all(t.type == TokenType.COLOR for t in tokens)
```

### Test W3C Exporter (In Isolation)

```python
# tests/exporters/test_w3c_exporter.py
# ✅ Can test without any other exporter
# ✅ Can mock TokenGraph

import pytest
from copy_that.exporters.w3c import W3CExporter
from copy_that.domain.tokens import TokenGraph, TokenRepository, Token, TokenType

@pytest.mark.asyncio
async def test_w3c_export():
    repo = TokenRepository()
    token = Token(id="color/01", type=TokenType.COLOR, value="#FF0000", attributes={})
    repo.add_token(token)

    graph = TokenGraph(repo)
    exporter = W3CExporter()
    result = await exporter.export(graph)

    assert "color" in result
    assert "color/01" in result["color"]
```

### Test Service (Uses Registry)

```python
# tests/services/test_extraction_service.py
# ✅ Can test orchestration without caring which extractors are registered
# ✅ Can mock get_extractor if needed

import pytest
from copy_that.services.extraction_service import ExtractionService
from copy_that.domain.tokens import TokenRepository

@pytest.mark.asyncio
async def test_extraction_orchestration():
    repo = TokenRepository()
    service = ExtractionService(repo)

    graph = await service.extract_tokens(
        "base64_image",
        token_types=["color", "spacing"]
    )

    assert graph is not None
    assert len(graph.repo.all_tokens()) > 0
```

---

## Verification: Zero-Coupling Checklist

```bash
# Script to verify no circular imports or cross-module imports
python -m py_compile src/copy_that/extractors/color/__init__.py
# Should NOT import any module from:
# - src/copy_that/extractors/spacing/
# - src/copy_that/extractors/typography/
# - src/copy_that/exporters/
# - src/copy_that/services/ (except base if needed)
# - src/copy_that/interfaces/api/

python -m py_compile src/copy_that/exporters/w3c/__init__.py
# Should NOT import any module from:
# - src/copy_that/exporters/tailwind/
# - src/copy_that/exporters/css/
# - src/copy_that/extractors/
# - src/copy_that/interfaces/api/
```

---

## Coupling Metrics

| Metric | Target | Method |
|--------|--------|--------|
| **Module imports** | ≤ 5 per module | Count imports (exclude base, domain) |
| **Cross-module imports** | 0 | All imports from extractors.* or exporters.* forbidden |
| **Circular dependencies** | 0 | Run `python -m pydeps` |
| **Service testability** | ✅ | Can instantiate with mock TokenRepository |
| **Extractor testability** | ✅ | Can test in isolation with mock image |
| **Exporter testability** | ✅ | Can test with mock TokenGraph |

---

## Summary: The Zero-Coupling Guarantee

✅ **No module knows about other modules' implementations**
✅ **Services use registries, not direct imports**
✅ **Each module depends only on base interfaces and domain models**
✅ **Circular dependencies impossible**
✅ **New modules can be added without changing existing code**
✅ **Each module can be developed, tested, and deployed independently**
✅ **Registry is the single point of module registration**
✅ **API is pure HTTP translation with no business logic**

This is how **professional platforms** (Figma, Storybook, Design System tools) achieve modularity at scale.
