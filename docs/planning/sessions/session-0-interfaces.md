# Session 0: Pipeline Interfaces

**Run First - Blocks All Other Sessions**

## Branch
```bash
git checkout -b claude/pipeline-interfaces-{SESSION_ID}
```

## Mission
Establish shared interfaces and types for all pipeline agents with W3C Design Tokens support. This MUST complete before other sessions begin.

## Architecture Context

### Terminology (IMPORTANT)

| Layer | Pattern | Responsibility |
|-------|---------|----------------|
| Pipeline | `{Stage}Agent` | Orchestration & health management |
| Application | `{Type}Extractor` | Actual token extraction (AI-powered) |
| Integration | `{Type}Adapter` | Schema transformation |
| Output | `{Format}Generator` | Code generation |

**"Agent"** represents orchestration/coordination. **"Extractor"** handles actual extraction. These are distinct concerns that coexist. See [PIPELINE_GLOSSARY.md](../../architecture/PIPELINE_GLOSSARY.md).

## Owned Files

Create these files:
- `src/copy_that/pipeline/__init__.py`
- `src/copy_that/pipeline/interfaces.py`
- `src/copy_that/pipeline/types.py`
- `src/copy_that/pipeline/exceptions.py`
- `tests/unit/pipeline/test_interfaces.py`
- `tests/unit/pipeline/test_types.py`

## Priority Tasks

### IMMEDIATE

#### 1. Types (`types.py`)

**Enums:**
- `TokenType` enum: color, spacing, typography, shadow, gradient (extraction categories)
- `W3CTokenType` enum: color, dimension, fontFamily, fontWeight, duration, cubicBezier, number, strokeStyle, border, transition, shadow, gradient, typography, composition

**Models:**
- `TokenResult` Pydantic model with W3C support:
  - `token_type: TokenType` - extraction category
  - `name: str` - token name
  - `path: list[str]` - hierarchy path (e.g., ["color", "brand"])
  - `w3c_type: W3CTokenType | None` - W3C $type
  - `value: str | int | float | bool | dict` - simple or composite
  - `description: str | None` - W3C $description
  - `reference: str | None` - token reference (e.g., "{color.primary}")
  - `confidence: float` - 0.0-1.0
  - `extensions: dict | None` - W3C $extensions
  - `metadata: dict | None` - internal metadata
  - `full_path` property - dot-separated path
  - `to_w3c_dict()` method - W3C export

- `PipelineTask` model
- `ProcessedImage` model

**TESTS FIRST**

#### 2. Interfaces (`interfaces.py`)
- BasePipelineAgent ABC
- Methods: `process()`, `health_check()`
- Properties: `agent_type`, `stage_name`
- **TESTS FIRST**

#### 3. Exceptions (`exceptions.py`)
- PipelineError (base)
- PreprocessingError
- ExtractionError
- AggregationError
- ValidationError
- GenerationError
- **TESTS FIRST**

## W3C Design Tokens Support

TokenResult supports full W3C Design Tokens format for export:

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
# Returns: {"$value": "#FF6B35", "$type": "color", "$description": "...", "$extensions": {...}}
```

## Integration Pattern

Agents should **wrap existing extractors**:

```python
class ColorExtractionAgent(BasePipelineAgent):
    def __init__(self):
        self._extractor = AIColorExtractor()  # Wrap existing

    async def process(self, task: PipelineTask) -> list[TokenResult]:
        result = await asyncio.to_thread(
            self._extractor.extract_colors_from_image_url,
            task.image_url
        )
        return [self._transform(c) for c in result.colors]
```

## Exit Criteria
- [x] All tests written BEFORE implementation
- [x] 100% test coverage for pipeline module
- [x] W3C Design Tokens support in TokenResult
- [x] Ready for other sessions to import

## Commit Message
```
feat: add pipeline interfaces and types with W3C support
```

## Auto-Execute
1. Create branch
2. Write tests
3. Implement
4. Commit and push

## Documentation
- [PIPELINE_GLOSSARY.md](../../architecture/PIPELINE_GLOSSARY.md) - Terminology and patterns
- [ADAPTER_PATTERN.md](../../architecture/ADAPTER_PATTERN.md) - Schema transformation
- [EXTRACTOR_PATTERNS.md](../../architecture/EXTRACTOR_PATTERNS.md) - Existing extractors
