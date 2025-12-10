# Metrics Architecture Refactoring Handoff

**Date:** 2025-12-10
**Status:** Foundation Complete, Architecture Redesign Needed
**Progress:** ~85K tokens spent

---

## What Was Completed ✅

### 1. Pluggable Provider System (DONE)
Created the foundation for non-blocking, streaming metrics:

**Files Created:**
- `src/copy_that/services/metrics/__init__.py` - Module exports
- `src/copy_that/services/metrics/base.py` - MetricProvider abstract base + MetricTier enum + MetricResult
- `src/copy_that/services/metrics/registry.py` - MetricProviderRegistry for auto-discovery
- `src/copy_that/services/metrics/orchestrator.py` - MetricsOrchestrator with async streaming

**Key Design Decisions:**
- ✅ Non-blocking: Providers emit as ready, don't wait for others
- ✅ Composable: New providers just implement MetricProvider
- ✅ Multi-client: Backend orchestrates, any client consumes SSE stream
- ✅ Error-resilient: One provider failing doesn't block others

### 2. Initial Providers (PARTIAL)
Started implementing TIER 1 & 2 providers:

**Files Created:**
- `src/copy_that/services/metrics/quantitative.py` - TIER 1 (fast, deterministic)
- `src/copy_that/services/metrics/accessibility.py` - TIER 2 (WCAG, colorblind)

**Status:** These are **hardcoded to color/spacing/typography/shadow** - need redesign below.

---

## Critical Issue Identified 🚨

The current provider implementation is **too rigid** for multi-in, multi-out architecture:

```python
# Current approach (WRONG for scale):
colors = await self._fetch_colors(project_id)
spacing = await self._fetch_spacing(project_id)
typography = await self._fetch_typography(project_id)
shadows = await self._fetch_shadows(project_id)
```

**Problems:**
1. ❌ Hardcoded to specific token types (color, spacing, typography, shadow)
2. ❌ Won't scale to material, shape, components, artistic style tokens
3. ❌ No token graph traversal - doesn't understand relationships
4. ❌ Not ready for multimodal (audio tokens, video tokens, etc.)

---

## Required Redesign 🔧

### Phase 1: Generic Token System

**Goal:** Fetch ANY token type, understand token graph relationships

**Approach:**

```python
# 1. Generic token fetching
class TokenGraph:
    """Represents all tokens + their relationships for a project"""
    def __init__(self, project_id: int, db: AsyncSession):
        self.project_id = project_id
        self.db = db
        self.tokens: dict[str, TokenNode] = {}  # By fully-qualified name
        self.graph: nx.DiGraph = nx.DiGraph()   # Relationships

    async def load(self):
        """Load all tokens and build graph"""
        # Fetch from database using generic query
        all_tokens = await self._fetch_all_tokens()
        for token in all_tokens:
            self._add_token_node(token)
            self._add_relationships(token)

    def get_tokens_by_category(self, category: str) -> list[TokenNode]:
        """Get all tokens in a category (color, spacing, material, etc.)"""
        return [t for t in self.tokens.values() if t.category == category]

    def get_token_scale(self, base_name: str) -> list[TokenNode]:
        """Get related tokens (e.g., color.primary.light, .dark, .xlight)"""
        return [t for t in self.tokens.values() if self.graph.has_path(base_name, t.name)]

# 2. Token metadata
class TokenNode:
    """A single token in the graph"""
    name: str  # e.g., "token/color/primary/light"
    category: str  # e.g., "color", "spacing", "material", "shape"
    value: Any  # The actual value
    metadata: dict[str, Any]  # Type-specific data
    references: list[str]  # Other tokens this references
```

### Phase 2: Generic Metrics Provider

```python
class TokenEcosystemMetricsProvider(MetricProvider):
    """Analyzes ANY token type + their relationships (TIER 1)"""

    async def compute(self, project_id: int) -> MetricResult:
        # Load token graph
        graph = TokenGraph(project_id, self.db)
        await graph.load()

        # Analyze structure, not specific types
        metrics = {
            "total_tokens": len(graph.tokens),
            "categories": self._analyze_categories(graph),
            "hierarchies": self._analyze_hierarchies(graph),
            "scales": self._analyze_scales(graph),
            "relationships": self._analyze_relationships(graph),
            "organization_quality": self._assess_organization(graph),
        }
        return MetricResult(...)

    def _analyze_categories(self, graph: TokenGraph) -> dict:
        """What categories exist? How many tokens in each?"""
        return {
            category: {
                "count": len(graph.get_tokens_by_category(category)),
                "hierarchical": self._is_hierarchical(category),
            }
            for category in self._extract_categories(graph)
        }
```

### Phase 3: Specialized Metrics Providers

Each builds on TokenGraph but specializes:

```python
class ColorMetricsProvider(MetricProvider):
    """Color-specific metrics (contrast, harmony, etc.)"""
    async def compute(self, project_id: int):
        graph = TokenGraph(project_id, self.db)
        await graph.load()
        colors = graph.get_tokens_by_category("color")
        # Analyze relationships between color tokens

class MaterialMetricsProvider(MetricProvider):
    """Material-specific metrics (texture, finish, etc.)"""
    # Same pattern, but for material tokens

class AudioMetricsProvider(MetricProvider):
    """Audio token metrics (future - multimodal)"""
    # Same pattern, extensible to any modality
```

---

## Next Steps (for Sonnet)

1. **Refactor Token Fetching** (~2 hours)
   - Create `TokenGraph` class to load all tokens
   - Generic query (not hardcoded types)
   - Build relationship graph using NetworkX
   - Tests for graph construction

2. **Redesign Quantitative Provider** (~1.5 hours)
   - Use `TokenGraph` instead of hardcoded fetches
   - Analyze ANY token categories
   - Detect hierarchies/scales automatically
   - Remove assumptions about token types

3. **Complete Accessibility Provider** (~1 hour)
   - Update to work with TokenGraph
   - Works only on "color" category tokens
   - Remains specialized but generic about other categories

4. **Add QualitativeMetricsProvider** (~1-2 hours)
   - Phase 3 AI insights
   - Also uses TokenGraph

5. **Streaming Endpoint** (~1 hour)
   - Wire up orchestrator
   - SSE streaming

6. **Frontend** (~1-2 hours)
   - Remove NarrativeCards duplication
   - Consume SSE stream

---

## Files to Keep / Modify

**Keep (Good Foundation):**
- ✅ `metrics/base.py` - No changes needed
- ✅ `metrics/registry.py` - No changes needed
- ✅ `metrics/orchestrator.py` - No changes needed

**Refactor (Need Redesign):**
- ⚠️ `metrics/quantitative.py` - Replace with TokenGraph-based approach
- ⚠️ `metrics/accessibility.py` - Update to use TokenGraph

**Create (New):**
- 🆕 `metrics/token_graph.py` - TokenGraph class + TokenNode
- 🆕 `metrics/qualitative.py` - QualitativeMetricsProvider (TIER 3)
- 🆕 `interfaces/api/metrics_streaming.py` - Streaming endpoint

---

## Architecture Benefits (Why This Matters)

```
Current (BROKEN):           Redesigned (CORRECT):
┌─ color ────┐             ┌─ TokenGraph ─────────┐
├─ spacing   ├─ Metrics    │  any categories       │
├─ typography             │  any relationships    │
└─ shadow ───┘             └─ Metrics ────────────┘
                                 ↓
                           Works for:
                           • Color, Spacing, Typography, Shadow
                           • Material, Shape, Components
                           • AudioToken, VideoToken, etc.
                           • Custom token types
```

---

## Commit Strategy

Before handing off to Sonnet:

```bash
# Save current foundation (even though incomplete)
git add src/copy_that/services/metrics/base.py
git add src/copy_that/services/metrics/registry.py
git add src/copy_that/services/metrics/orchestrator.py
git commit -m "refactor: Add pluggable metrics provider foundation

- MetricProvider abstract base for composable metrics
- MetricProviderRegistry for auto-discovery
- MetricsOrchestrator for non-blocking streaming
- Foundation ready for multi-in, multi-out architecture

Note: Quantitative/Accessibility providers need redesign
to support generic token types (material, shape, components, etc.)
and multimodal tokens (audio, video, etc.)"
```

---

## Questions for Sonnet Session

1. **TokenGraph Design:** Use NetworkX or simpler approach?
2. **Token Categories:** Predefined list or fully dynamic?
3. **Multimodal Support:** Start abstracting audio/video token handling now?
4. **Token Metadata:** What fields should all tokens have (category, type, value, references)?
