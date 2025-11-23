# Session 3: Aggregation Pipeline

**Can Run in Parallel with Sessions 1-2, 4-5**

## Branch
```bash
git checkout -b claude/aggregation-pipeline-{SESSION_ID}
```

## Mission
Implement AggregationAgent: deduplicate, merge, track provenance across images.

## Owned Files

Create these files:
- `src/copy_that/pipeline/aggregation/__init__.py`
- `src/copy_that/pipeline/aggregation/agent.py`
- `src/copy_that/pipeline/aggregation/deduplicator.py`
- `src/copy_that/pipeline/aggregation/provenance.py`
- `tests/unit/pipeline/aggregation/test_agent.py`
- `tests/unit/pipeline/aggregation/test_deduplicator.py`

## Priority Tasks

### IMMEDIATE

#### 1. Deduplicator using Delta-E
- Use ColorAide library
- Threshold 2.0 JND (Just Noticeable Difference)
- Merge similar colors
- **TESTS FIRST**

#### 2. ProvenanceTracker
- Track which images contributed each token
- Calculate weighted confidence scores
- **TESTS FIRST**

### HIGH

#### 3. AggregationAgent
- Orchestrate deduplicator + provenance
- Return merged token list

#### 4. Clustering
- K-means for related tokens
- Group similar values

## Exit Criteria
- [ ] Delta-E deduplication works correctly
- [ ] Provenance tracks all source images
- [ ] All tests written BEFORE implementation
- [ ] 95%+ coverage

## Commit Message
```
feat: implement aggregation pipeline with Delta-E dedup
```

## Auto-Execute
1. Create branch
2. Write tests
3. Implement
4. Commit and push
