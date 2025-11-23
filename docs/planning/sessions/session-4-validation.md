# Session 4: Validation Pipeline

**Can Run in Parallel with Sessions 1-3, 5**

## Prerequisites
- **Session 0 MUST be complete** (pipeline interfaces)
- Import from `copy_that.pipeline`
- Validate `TokenResult` fields including W3C compliance
- See [PIPELINE_GLOSSARY.md](../../architecture/PIPELINE_GLOSSARY.md) for terminology

## Branch
```bash
git checkout -b claude/validation-pipeline-{SESSION_ID}
```

## Mission
Implement ValidationAgent: schema validation, accessibility scores, quality metrics.

## Owned Files

Create these files:
- `src/copy_that/pipeline/validation/__init__.py`
- `src/copy_that/pipeline/validation/agent.py`
- `src/copy_that/pipeline/validation/accessibility.py`
- `src/copy_that/pipeline/validation/quality.py`
- `tests/unit/pipeline/validation/test_agent.py`
- `tests/unit/pipeline/validation/test_accessibility.py`

## Priority Tasks

### IMMEDIATE

#### 1. Schema Validation with Pydantic
- Validate all token fields
- Check bounds (hex format, sizes > 0)
- **TESTS FIRST**

#### 2. AccessibilityCalculator
- WCAG contrast ratios (AA: 4.5:1, AAA: 7:1)
- Colorblind safety checks
- **TESTS FIRST**

### HIGH

#### 3. QualityScorer
- Confidence aggregation
- Completeness checks

#### 4. ValidationAgent
- Orchestrate all validation steps
- Return validated tokens with scores

## Exit Criteria
- [ ] All token schemas validated
- [ ] WCAG scores calculated correctly
- [ ] All tests written BEFORE implementation
- [ ] 95%+ coverage

## Commit Message
```
feat: implement validation pipeline with WCAG scoring
```

## Auto-Execute
1. Create branch
2. Write tests
3. Implement
4. Commit and push
