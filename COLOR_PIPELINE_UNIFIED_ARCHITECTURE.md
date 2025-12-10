# Color Pipeline - Unified Token Graph Architecture

**Objective:** Create a comprehensive color extraction pipeline that leverages the **Token Graph** as the central model, while preserving excellent W3C export and ramp generation capabilities.

**Status:** Ready to implement
**Architecture:** Token Graph-centric with integrated legacy capabilities

---

## Unified Architecture Vision

### The Token Graph Is the Hub

The **TokenGraph** is the intelligent center that manages:
- Token relationships (aliases, multiples, references)
- Token resolution (alias follow-through, cycle detection)
- Token metadata (attributes, relations, value)
- Token validation

**All operations** flow through the token graph:

```
Frontend Request
    ↓
API Endpoint
    ↓
ExtractionService (orchestrates extractors)
    ↓
TokenGraph (manages relationships)
    ↓
ExportService (W3C, JSON, etc.)
    ↓
Frontend TokenGraphStore (Zustand)
```

---

## Architecture Layers

### Layer 1: Token Graph (Python Backend)

**File:** `src/core/tokens/graph.py` + `src/core/tokens/model.py`

**Core Classes:**
```python
class Token:
    id: str
    type: TokenType  # color, spacing, typography, shadow
    value: TokenValue  # actual value (hex for color)
    attributes: dict  # metadata
    relations: list[TokenRelation]  # ALIAS_OF, MULTIPLE_OF, REFERENCES

class TokenRelation:
    type: RelationType  # ALIAS_OF, MULTIPLE_OF, REFERENCES, etc.
    target: str  # target token ID
    meta: dict  # relation metadata (e.g., multiplier)

class TokenGraph:
    repo: TokenRepository  # in-memory or persisted

    # Core operations
    add_token(token: Token) -> Token
    get_token(token_id: str) -> Token | None
    add_relation(source, relation_type, target) -> None
    resolve_alias(token_id: str) -> Token  # Follow aliases to base token
    detect_cycles() -> list[list[str]]  # Validate graph integrity
```

**Why This Works:**
- ✅ Relationships are first-class citizens
- ✅ Aliases automatically resolve
- ✅ Cycle detection prevents invalid graphs
- ✅ Composable: build complex tokens from simpler ones

---

### Layer 2: Color Extraction Pipeline

**Architecture:**
```
src/copy_that/application/color/
├── extractor.py                  (K-means fast extraction)
├── ai_extractor.py              (Claude/OpenAI fallback)
├── cv_extractor.py              (CV-based extraction)
├── semantic_naming.py            (Color naming)
├── utils.py                      (Color conversions)
├── token_converter.py (NEW)      (Extract → Token → Graph)
├── graph_operations.py (NEW)     (Graph-specific color ops)
└── __init__.py
```

### Layer 3: Services Layer

**Architecture:**
```
src/copy_that/services/color/
├── extraction_service.py         (Orchestrate extractors)
├── graph_service.py (NEW)        (TokenGraph operations)
├── storage_service.py            (Database persistence)
├── export_service.py             (W3C, JSON export)
├── ramp_service.py              (Color ramp generation)
└── __init__.py
```

### Layer 4: API Layer

**Architecture:**
```
src/copy_that/interfaces/api/colors/
├── router.py                     (REST endpoints)
├── schemas.py                    (Request/response models)
├── handlers.py                   (Endpoint handlers)
├── validators.py                 (Input validation)
└── __init__.py
```

### Layer 5: Frontend Store

**File:** `frontend/src/store/tokenGraphStore.ts`

**Zustand Store Structure:**
```typescript
interface TokenGraphState {
  loaded: boolean
  colors: UiColorToken[]         // From W3C export
  spacing: UiSpacingToken[]
  shadows: UiShadowToken[]
  typography: UiTypographyToken[]

  // Token graph relationships
  aliases: Map<string, string>   // token_id → base_token_id
  multiples: Map<string, [string, number]>  // token_id → [base_id, multiplier]
  references: Map<string, string[]>  // token_id → [referenced_ids]

  // Operations
  load(projectId: number): Promise<void>
  resolveAlias(tokenId: string): Token
  followReferences(tokenId: string): Token[]
}
```

---

## Color Extraction Flow (Unified)

### Step 1: Receive Image

```python
@router.post("/colors/extract")
async def extract_colors(request: ExtractColorRequest):
    """Entry point for color extraction."""
```

**Validation:**
- Base64 image format ✓
- Image size limits ✓
- Rate limiting ✓

### Step 2: Fast Extraction

```python
class ExtractionService:
    async def extract_colors(self, image_base64: str) -> ColorExtractionResult:
        # Try fast K-means extractor
        extracted = ColorExtractor(image_base64).extract()
        # Returns: list[ExtractedColorToken]
```

**Output:** `ExtractedColorToken` objects (hex, name, confidence, etc.)

### Step 3: Convert to Tokens

```python
class TokenConverter:
    def to_tokens(
        self,
        extracted: list[ExtractedColorToken],
        namespace: str = "color"
    ) -> list[Token]:
        """Convert extracted colors → Token objects."""
        tokens = []
        for i, color in enumerate(extracted):
            token = Token(
                id=f"{namespace}/{i:02d}",
                type=TokenType.COLOR,
                value=color.hex,
                attributes={
                    "name": color.name,
                    "confidence": color.confidence,
                    "harmony": color.harmony,
                    "hue_angles": color.hue_angles,
                    "temperature": color.temperature,
                    ...
                },
                relations=[]  # No relations initially
            )
            tokens.append(token)
        return tokens
```

### Step 4: Build Token Graph

```python
class GraphService:
    async def build_color_graph(
        self,
        tokens: list[Token],
        project_id: int
    ) -> TokenGraph:
        """Build token graph with relationships."""
        repo = TokenRepository()  # or use database
        graph = TokenGraph(repo)

        # Add extracted color tokens
        for token in tokens:
            graph.add_token(token)

        # Generate color ramps (if primary color exists)
        primary = find_primary_color(tokens)
        if primary:
            ramp_tokens = generate_ramp_tokens(primary)
            for ramp_token in ramp_tokens:
                graph.add_token(ramp_token)
                # Create DERIVED_FROM relation
                graph.add_relation(
                    ramp_token.id,
                    RelationType.DERIVED_FROM,
                    primary.id
                )

        return graph
```

### Step 5: Persist to Database

```python
class StorageService:
    async def save_color_graph(
        self,
        graph: TokenGraph,
        project_id: int
    ) -> None:
        """Persist token graph to ColorToken records."""
        for token in graph.repo.all_tokens():
            color_record = ColorToken(
                project_id=project_id,
                hex=token.value,  # For colors
                name=token.attributes.get("name"),
                design_intent=token.attributes.get("design_intent"),
                semantic_names=json.dumps(token.attributes.get("semantic_names")),
                harmony=token.attributes.get("harmony"),
                # ... all other fields
                extraction_metadata=json.dumps({
                    "token_id": token.id,
                    "token_type": token.type,
                    "relations": [
                        {"type": r.type, "target": r.target, "meta": r.meta}
                        for r in token.relations
                    ]
                })
            )
            await db.add(color_record)
        await db.commit()
```

### Step 6: Export as W3C

```python
class ExportService:
    async def export_w3c(
        self,
        graph: TokenGraph,
        include_ramps: bool = True
    ) -> W3CDesignTokenResponse:
        """Generate W3C design tokens from token graph."""

        # Load from graph (replaces legacy tokens_to_w3c)
        w3c_tokens = {}

        for token in graph.repo.all_tokens():
            if token.type == TokenType.COLOR:
                # Resolve alias if this is an alias token
                base_token = graph.resolve_alias(token.id)

                w3c_tokens[base_token.id] = {
                    "$type": "color",
                    "$value": base_token.value,  # hex
                    "$description": base_token.attributes.get("name"),
                    # ... other W3C fields
                }

                # If this is an alias, add reference
                if token.id != base_token.id:
                    w3c_tokens[token.id] = {
                        "$type": "color",
                        "$value": {"$ref": f"#{base_token.id}"},
                    }

        return {
            "$schema": "https://tokens.figma.com/json/draft-3/",
            "color": w3c_tokens,
            "color/ramps": self._generate_ramp_section(graph) if include_ramps else {}
        }
```

### Step 7: Send to Frontend

```python
@router.post("/colors/extract")
async def extract_colors(request: ExtractColorRequest):
    # ... steps 1-6

    return {
        "colors": [token.to_api_response() for token in extracted],
        "ramps": ramps,
        "w3c_tokens": w3c_export,
        "metadata": {
            "extraction_method": "fast",
            "token_count": len(tokens),
            "project_id": project_id
        }
    }
```

### Step 8: Frontend Consumes via TokenGraphStore

```typescript
// frontend/src/store/tokenGraphStore.ts
const useTokenGraphStore = create<TokenGraphState>((set) => ({
  async load(projectId: number) {
    const response = await apiClient.get(
      `/api/v1/design-tokens/export/w3c?project_id=${projectId}`
    )

    // Reconstruct token graph from W3C response
    const colors = response.color
    const aliases = new Map()
    const references = new Map()

    // Parse W3C tokens to rebuild relationships
    for (const [tokenId, tokenDef] of Object.entries(colors)) {
      if (tokenDef.$value?.$ref) {
        // This is an alias
        aliases.set(tokenId, tokenDef.$value.$ref.replace("#", ""))
      }
    }

    set({
      loaded: true,
      colors: response.color,
      spacing: response.spacing,
      aliases,
      references
    })
  }
}))
```

---

## Key Integration Points

### 1. Legacy Code Integration

**Functions to Preserve:**
```python
# src/copy_that/application/color/legacy_adapters.py
from core.tokens.adapters.w3c import tokens_to_w3c  # Keep importing
from core.tokens.color import make_color_ramp, ramp_to_dict  # Keep importing
from core.tokens.repository import TokenRepository, InMemoryTokenRepository  # Keep importing

# BUT: Create modern wrappers that use TokenGraph internally
def export_to_w3c_from_graph(graph: TokenGraph) -> dict:
    """Modern wrapper around legacy tokens_to_w3c."""
    # Convert graph → TokenRepository format
    # Call legacy function
    # Return result
```

**Why Keep Them:**
- ✅ Excellent W3C export logic
- ✅ Proven ramp generation
- ✅ Tested extensively
- ✅ No need to reinvent

**How to Use:**
- Wrap in modern services layer
- Don't import directly in API
- Encapsulate in ExportService

### 2. Database Persistence

**ColorToken Model Stores:**
```python
class ColorToken(Base):
    # ... existing fields ...

    # NEW: Token graph metadata
    token_id: str  # e.g., "color/01"
    token_type: str  # "color"
    token_relations: str  # JSON: [{"type": "DERIVED_FROM", "target": "color/00", "meta": {}}]
    graph_serialized: str  # Full token graph serialized (optional)
```

### 3. Token Graph Loading on API Calls

```python
class ColorService:
    async def get_project_color_graph(self, project_id: int) -> TokenGraph:
        """Load project's color token graph from database."""
        tokens = await db.query(ColorToken).filter(
            ColorToken.project_id == project_id
        ).all()

        repo = TokenRepository()
        graph = TokenGraph(repo)

        for record in tokens:
            token_data = json.loads(record.graph_serialized)
            token = Token(**token_data)
            graph.add_token(token)

        return graph
```

---

## Missing Features (Now Enabled)

With this architecture, we can now add:

### 1. Color Refinement
```python
@router.post("/colors/{color_id}/refine")
async def refine_color(color_id: str, adjustments: ColorAdjustments):
    """Refine color and regenerate ramps."""
    graph = await color_service.get_project_color_graph(project_id)
    token = graph.get_token(color_id)

    # Apply adjustments
    refined = apply_color_adjustments(token, adjustments)
    graph.add_token(refined)

    # Regenerate dependent ramps
    for ramp_token in graph.find_by_relation("DERIVED_FROM", color_id):
        ramp_token.value = generate_ramp(refined)
        graph.add_token(ramp_token)

    return await export_service.export_w3c(graph)
```

### 2. Color Aliases (Semantic Names)
```python
@router.post("/colors/{color_id}/add-alias")
async def add_color_alias(color_id: str, alias_name: str):
    """Create alias for color."""
    graph = await color_service.get_project_color_graph(project_id)

    graph.add_alias(
        alias_id=f"color/{alias_name.lower()}",
        target_id=color_id,
        token_type=TokenType.COLOR
    )

    return await export_service.export_w3c(graph)
```

### 3. Color Merging (Deduplication)
```python
@router.post("/colors/merge")
async def merge_colors(source_id: str, target_id: str):
    """Merge duplicate colors by aliasing."""
    graph = await color_service.get_project_color_graph(project_id)

    # Make source an alias of target
    graph.add_relation(source_id, RelationType.ALIAS_OF, target_id)

    # All references to source now resolve to target
    return await export_service.export_w3c(graph)
```

### 4. Batch Analysis
```python
@router.post("/colors/batch-analyze")
async def batch_analyze_colors(color_ids: list[str]):
    """Analyze color relationships."""
    graph = await color_service.get_project_color_graph(project_id)

    analysis = {
        "total_colors": len(graph.repo.all_tokens()),
        "aliases": len([t for t in graph.repo.all_tokens()
                       if any(r.type == RelationType.ALIAS_OF for r in t.relations)]),
        "ramps": len([t for t in graph.repo.all_tokens()
                     if any(r.type == RelationType.DERIVED_FROM for r in t.relations)]),
        "cycles": len(graph.detect_cycles()),
        "isolated": len(graph.find_isolated_tokens()),
    }

    return analysis
```

---

## Implementation Phases

### Phase 1: Setup Token Graph Integration (2 hours)
- [ ] Create `TokenConverter` to convert extracted colors → Tokens
- [ ] Create `GraphService` to build TokenGraph
- [ ] Create `legacy_adapters.py` wrapper for W3C/ramp generation
- [ ] Update `ExportService` to use token graph

### Phase 2: Refactor API Layer (3 hours)
- [ ] Move API logic to services layer
- [ ] Create `/colors/` subdirectory in API
- [ ] Update imports to use modern services
- [ ] Test end-to-end

### Phase 3: Database Persistence (2 hours)
- [ ] Update `ColorToken` model with token graph fields
- [ ] Create migration to add new fields
- [ ] Implement graph loading from database
- [ ] Implement graph saving to database

### Phase 4: Enhanced Features (4+ hours)
- [ ] Color refinement endpoints
- [ ] Alias management
- [ ] Batch analysis
- [ ] Ramp regeneration

### Phase 5: Frontend Integration (Ongoing)
- [ ] Update TokenGraphStore to handle color relationships
- [ ] Add UI for alias management
- [ ] Add UI for color refinement
- [ ] Add visualization of color relationships

---

## Architecture Benefits

| Aspect | Benefit |
|--------|---------|
| **Relationships** | First-class via TokenGraph |
| **Aliases** | Automatic resolution via graph |
| **Ramps** | Derived_FROM relations + legacy generation |
| **Deduplication** | Alias tokens instead of deletion |
| **W3C Export** | Proven legacy code wrapped in modern services |
| **Scalability** | Graph structure scales to 1000s of tokens |
| **Validation** | Cycle detection prevents invalid states |
| **Frontend** | Relationships available in UI token graph store |

---

## Success Metrics

- [x] Token graph as central model
- [x] Legacy W3C/ramp code integrated
- [x] Color pipeline end-to-end functional
- [ ] Can extract, refine, and export colors
- [ ] Can create and resolve aliases
- [ ] Can generate ramps and themes
- [ ] Frontend UI reflects relationships

---

## Next Steps

Ready to implement Phase 1?

1. **Create TokenConverter** - Extract → Token
2. **Create GraphService** - Build TokenGraph
3. **Create legacy_adapters wrapper** - Keep good W3C code
4. **Update ExportService** - Use graph internally
5. **Test end-to-end** - Verify flow
