# Session 6: Pipeline Orchestrator

**Run After Sessions 1-5 Complete**

## Prerequisites
- **Sessions 0-5 MUST be complete**
> Legacy note: the `copy_that.pipeline` package has been removed; use token-graph modules instead.
- Coordinate all `BasePipelineAgent` implementations
- See [PIPELINE_GLOSSARY.md](../../architecture/PIPELINE_GLOSSARY.md) for terminology

## Branch
```bash
git checkout -b claude/pipeline-orchestrator-{SESSION_ID}
```

## Mission
Implement Orchestrator: coordinate pipeline agents, manage concurrency, circuit breakers.

## Owned Files

Create these files:
- `src/copy_that/pipeline/orchestrator/__init__.py`
- `src/copy_that/pipeline/orchestrator/coordinator.py`
- `src/copy_that/pipeline/orchestrator/agent_pool.py`
- `src/copy_that/pipeline/orchestrator/circuit_breaker.py`
- `tests/unit/pipeline/orchestrator/test_coordinator.py`
- `tests/unit/pipeline/orchestrator/test_agent_pool.py`
- `tests/unit/pipeline/orchestrator/test_circuit_breaker.py`

## Priority Tasks

### IMMEDIATE

#### 1. AgentPool with Semaphore
- Configurable concurrency per stage
- Task tracking (active, completed, failed)
- **TESTS FIRST**

#### 2. CircuitBreaker
- States: CLOSED → OPEN → HALF_OPEN
- Failure threshold (default 5)
- Recovery timeout (default 30s)
- **TESTS FIRST**

### HIGH

#### 3. PipelineCoordinator
- Execute: Preprocess → Extract → Aggregate → Validate → Generate
- Parallel image processing
- Error aggregation
- **TESTS FIRST**

## Pipeline Flow
```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│PREPROCESS│ → │ EXTRACT  │ → │AGGREGATE │ → │ VALIDATE │ → │ GENERATE │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

## Exit Criteria
- [ ] Concurrency limits enforced
- [ ] Circuit breaker prevents cascading failures
- [ ] Full pipeline executes correctly
- [ ] All tests written BEFORE implementation
- [ ] 95%+ coverage

## Commit Message
```
feat: implement pipeline orchestrator with circuit breakers
```

## Auto-Execute
1. Create branch
2. Write tests
3. Implement
4. Commit and push
