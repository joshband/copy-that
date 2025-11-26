# Pipeline Architecture Glossary

**Version:** 1.0
**Date:** 2025-11-23
**Status:** Active
The legacy `copy_that.pipeline` package has been removed; use token-graph models instead.

This document clarifies the terminology and architecture of the token extraction pipeline for all development sessions.

---

## Core Terminology

### Agent vs Extractor vs Adapter vs Generator

These terms represent **distinct architectural layers** with different responsibilities:

| Layer | Pattern | Responsibility | Example |
|-------|---------|----------------|---------|
| **Pipeline** | `{Stage}Agent` | Orchestration, health management, task routing | `ColorExtractionAgent` |
| **Application** | `{Type}Extractor` | Actual token extraction from images | `AIColorExtractor` |
| **Integration** | `{Type}Adapter` | Schema transformation between layers | `ColorTokenAdapter` |
| **Output** | `{Format}Generator` | Code generation in various formats | `W3CGenerator`, `CSSGenerator` |

### Why "Agent" and not "Processor"?

**"Agent"** was chosen deliberately to represent:
- **Orchestration**: Agents coordinate pipeline stages, not just process data
- **Health management**: Agents have `health_check()` for readiness verification
- **Identity**: Agents have `agent_type` and `stage_name` properties
- **Composition**: Multiple agents can work in parallel

**"Extractor"** is reserved for:
- **Data extraction**: Actually extracting tokens from images
- **AI integration**: Calling Claude/OpenAI APIs
- **Single responsibility**: One extractor per token type

---

## Pipeline Architecture

### Data Flow

```
┌──────────────┐     ┌─────────────────┐     ┌────────────────┐
│   Pipeline   │     │   Application   │     │   Output       │
│   Agents     │ ──► │   Extractors    │ ──► │   Generators   │
└──────────────┘     └─────────────────┘     └────────────────┘
      │                      │                       │
      │                      │                       │
      ▼                      ▼                       ▼
 Orchestration        Token Extraction         Code Generation
```

### Pipeline Stages

Agents operate in these sequential stages:

1. **Preprocessing** (`PreprocessingError`)
   - Image validation, resizing, format conversion
   - Generates `ProcessedImage` metadata

2. **Extraction** (`ExtractionError`)
   - AI-powered token extraction
   - Wraps existing extractors (AIColorExtractor, etc.)
   - Returns `TokenResult` objects

3. **Aggregation** (`AggregationError`)
   - Combine results from multiple extractors
   - Deduplicate similar tokens (Delta-E)
   - Merge confidence scores

4. **Validation** (`ValidationError`)
   - Validate token values and relationships
   - Check W3C compliance
   - Verify references resolve

5. **Generation** (`GenerationError`)
   - Generate output code (W3C, CSS, React, etc.)
   - Build token hierarchies
   - Export to files

---

## Type System

### TokenType (Extraction Categories)

Used to specify **what to extract** from an image:

```python
class TokenType(str, Enum):
    COLOR = "color"        # Hex colors, RGB values
    SPACING = "spacing"    # Margins, padding, gaps
    TYPOGRAPHY = "typography"  # Fonts, sizes, weights
    SHADOW = "shadow"      # Box shadows, drop shadows
    GRADIENT = "gradient"  # Linear, radial gradients
```

### W3CTokenType (Output Format)

Used to specify the **W3C $type** in exports:

```python
class W3CTokenType(str, Enum):
    # Primitive types
    COLOR = "color"
    DIMENSION = "dimension"
    FONT_FAMILY = "fontFamily"
    FONT_WEIGHT = "fontWeight"
    DURATION = "duration"
    CUBIC_BEZIER = "cubicBezier"
    NUMBER = "number"

    # Composite types
    SHADOW = "shadow"
    GRADIENT = "gradient"
    TYPOGRAPHY = "typography"
    COMPOSITION = "composition"
```

### Relationship

- `TokenType.SPACING` → `W3CTokenType.DIMENSION` (for px/rem values)
- `TokenType.COLOR` → `W3CTokenType.COLOR`
- `TokenType.TYPOGRAPHY` → `W3CTokenType.TYPOGRAPHY` (composite)

---

## W3C Design Tokens Support

### TokenResult Fields

The `TokenResult` model supports full W3C Design Tokens format:

```python
class TokenResult(BaseModel):
    # Extraction context
    token_type: TokenType      # What was extracted (color, spacing, etc.)
    name: str                  # Token name (final path segment)

    # W3C core fields
    path: list[str]           # Hierarchy: ["color", "brand"]
    w3c_type: W3CTokenType    # $type: "color", "dimension", etc.
    value: str | dict         # $value: "#FF6B35" or composite
    description: str | None   # $description: Human-readable
    reference: str | None     # Token reference: "{color.primary}"
    extensions: dict | None   # $extensions: Vendor metadata

    # Extraction metadata
    confidence: float         # 0.0-1.0 confidence score
    metadata: dict | None     # Internal extraction metadata
```

### W3C Export

Use `to_w3c_dict()` for W3C-compliant JSON:

```python
result = TokenResult(
    token_type=TokenType.COLOR,
    name="primary",
    path=["color", "brand"],
    w3c_type=W3CTokenType.COLOR,
    value="#FF6B35",
    confidence=0.95,
    description="Primary brand color"
)

# Export to W3C format
w3c = result.to_w3c_dict()
# {
#   "$value": "#FF6B35",
#   "$type": "color",
#   "$description": "Primary brand color",
#   "$extensions": {
#     "com.copythat": {"confidence": 0.95, "extractionType": "color"}
#   }
# }
```

---

## Integration Pattern

### Wrapper Pattern for Agents

Agents should **wrap existing extractors**, not replace them:

```python
The legacy `copy_that.pipeline` package has been removed. Use the token-graph modules (`core.tokens.*`) and `pipeline/panel_to_tokens.py` instead.
from copy_that.application.color_extractor import AIColorExtractor

class ColorExtractionAgent(BasePipelineAgent):
    """Pipeline agent that wraps AIColorExtractor."""

    def __init__(self):
        self._extractor = AIColorExtractor()

    @property
    def agent_type(self) -> str:
        return "color_extractor"

    @property
    def stage_name(self) -> str:
        return "extraction"

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        # Delegate to existing extractor
        import asyncio
        result = await asyncio.to_thread(
            self._extractor.extract_colors_from_image_url,
            task.image_url,
            task.context.get("max_colors", 10) if task.context else 10
        )

        # Transform to TokenResult
        return [
            TokenResult(
                token_type=TokenType.COLOR,
                name=color.name,
                w3c_type=W3CTokenType.COLOR,
                value=color.hex,
                confidence=color.confidence,
                metadata={
                    "rgb": color.rgb,
                    "harmony": color.harmony,
                    "temperature": color.temperature,
                }
            )
            for color in result.colors
        ]

    async def health_check(self) -> bool:
        return self._extractor.client is not None
```

---

## Exception Hierarchy

All pipeline exceptions inherit from `PipelineError`:

```python
class PipelineError(Exception):
    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details

class PreprocessingError(PipelineError): pass  # Image processing failures
class ExtractionError(PipelineError): pass     # Token extraction failures
class AggregationError(PipelineError): pass    # Merging/dedup failures
class ValidationError(PipelineError): pass     # Token validation failures
class GenerationError(PipelineError): pass     # Code generation failures
```

Each exception includes:
- `message`: Human-readable error description
- `details`: Dict with task_id, image_url, and error context

---

## Session Guidelines

### For Sessions 1-6

When implementing agents, follow these patterns:

1. **Wrap, don't replace**: Use existing extractors as the core logic
2. **Transform to TokenResult**: Convert extractor output to pipeline types
3. **Include W3C fields**: Set `w3c_type`, `path`, `description` for exports
4. **Handle errors**: Raise appropriate `PipelineError` subclasses
5. **Implement health_check**: Verify API keys, models, connections

### Imports

```python
    # Types
    TokenType,
    W3CTokenType,
    TokenResult,
    PipelineTask,
    ProcessedImage,
    # Interfaces
    BasePipelineAgent,
    # Exceptions
    PipelineError,
    PreprocessingError,
    ExtractionError,
    AggregationError,
    ValidationError,
    GenerationError,
)
```

---

## Related Documentation

- [Session 0: Pipeline Interfaces](../planning/sessions/session-0-interfaces.md)
- [Adapter Pattern](./ADAPTER_PATTERN.md)
- [Extractor Patterns](./EXTRACTOR_PATTERNS.md)
- [Strategic Vision](./STRATEGIC_VISION_AND_ARCHITECTURE.md)

---

## Summary

- **Agents** = Pipeline orchestration (wraps extractors)
- **Extractors** = Actual token extraction (AI-powered)
- **Adapters** = Schema transformation
- **Generators** = Code output

The distinction between Agent and Extractor is **intentional**. They serve different architectural purposes and should coexist.
