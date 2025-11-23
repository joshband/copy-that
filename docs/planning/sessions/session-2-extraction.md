# Session 2: Extraction Engine

**Can Run in Parallel with Sessions 1, 3-5**

## Prerequisites
- **Session 0 MUST be complete** (pipeline interfaces)
- Import from `copy_that.pipeline`
- Use `TokenResult` with W3C fields for output
- See [PIPELINE_GLOSSARY.md](../../architecture/PIPELINE_GLOSSARY.md) for terminology

## Branch
```bash
git checkout -b claude/extraction-engine-{SESSION_ID}
```

## Mission
Implement ExtractionAgent that extracts tokens using AI. Configurable for any token type via Tool Use schemas.

## Owned Files

Create these files:
- `src/copy_that/pipeline/extraction/__init__.py`
- `src/copy_that/pipeline/extraction/agent.py`
- `src/copy_that/pipeline/extraction/schemas.py`
- `src/copy_that/pipeline/extraction/prompts.py`
- `tests/unit/pipeline/extraction/test_agent.py`
- `tests/unit/pipeline/extraction/test_schemas.py`

## Priority Tasks

### IMMEDIATE

#### 1. Tool Use Schemas (`schemas.py`)
- Color schema
- Spacing schema
- Typography schema
- Shadow schema
- Gradient schema
- Strict JSON Schema validation
- **TESTS FIRST**

#### 2. ExtractionAgent Class
- Configurable by `token_type` parameter
- Uses Claude Tool Use (NO regex parsing)
- Handles timeout, rate limits, retries
- **TESTS FIRST** with mocked Anthropic client

### HIGH

#### 3. Prompt Templates
- One template per token type
- Clear instructions for AI

#### 4. Response Parsing
- Parse Tool Use response
- Validate against schema

## Key Principle
**Single agent handles ALL token types via configuration. NO separate ColorAgent, SpacingAgent, etc.**

## Exit Criteria
- [ ] Single agent handles all token types
- [ ] Uses Tool Use (NO regex parsing)
- [ ] All tests written BEFORE implementation
- [ ] 95%+ coverage

## Commit Message
```
feat: implement extraction engine with Tool Use
```

## Auto-Execute
1. Create branch
2. Write tests
3. Implement
4. Commit and push
