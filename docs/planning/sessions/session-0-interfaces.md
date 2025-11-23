# Session 0: Pipeline Interfaces

**Run First - Blocks All Other Sessions**

## Branch
```bash
git checkout -b claude/pipeline-interfaces-{SESSION_ID}
```

## Mission
Establish shared interfaces and types for all pipeline agents. This MUST complete before other sessions begin.

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
- TokenType enum: color, spacing, typography, shadow, gradient
- TokenResult Pydantic model
- PipelineTask model
- ProcessedImage model
- **TESTS FIRST**

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

## Exit Criteria
- [ ] All tests written BEFORE implementation
- [ ] 100% test coverage
- [ ] Ready for other sessions to import

## Commit Message
```
feat: add pipeline interfaces and types
```

## Auto-Execute
1. Create branch
2. Write tests
3. Implement
4. Commit and push
