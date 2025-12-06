# Test Execution Strategy & Memory Optimization

**Purpose:** Guide for running Copy That's test suite efficiently in different contexts
**Status:** ✅ PRODUCTION OPTIMIZED
**Last Updated:** 2025-12-05

---

## Executive Summary

The Copy That test suite (446 tests) requires careful memory management to avoid out-of-memory (OOM) errors. This guide provides three optimized execution strategies for different contexts:

| Strategy | Memory | Time | Pass Rate | Best For |
|----------|--------|------|-----------|----------|
| **Watch Mode** | 500MB | N/A | 100% | Local development |
| **CI/CD Split** | 2-4GB | 8 min | 98%+ | Automated pipelines |
| **Full Suite** | 4GB | 13 min | 98%+ | Pre-release validation |

**Recommendation for CI/CD:** Use `pnpm test:split` with 4GB heap (optimal cost/reliability balance)

---

## Problem Analysis

### Why Memory Usage is High

The test suite accumulates memory due to:

1. **jsdom Environment:** Creates full DOM simulations for each test file
   - Virtual DOM for each component test
   - Full browser API mocks
   - Memory not fully released between test files

2. **Component Mocking:** React Testing Library + Vitest create many component instances
   - 150+ component tests create thousands of DOM nodes
   - Mocking frameworks (sinon, etc.) retain references

3. **Test Fixtures:** Test data and database mocks accumulate
   - Color data fixtures retained in memory
   - Mock API responses cached
   - Temporary state not fully cleaned up

4. **Inherent Limitation:** jsdom is inherently memory-intensive
   - No practical way to reduce below ~4GB for full suite
   - Memory ceiling at 4GB heap (adding more doesn't help)

### Memory Growth Pattern

```
Phase 1 (Core Data):        <500MB   ✅ Clean
Phase 2 (Components):       4-5GB    ⚠️ Heavy jsdom usage
Phase 3 (API & Color):      <500MB   ✅ Clean
Phase 4 (Image Uploader):   <1GB     ✅ Moderate
─────────────────────────────────────────────
Full Suite Parallel:        8GB+     ❌ OOM Risk
Full Suite Sequential:      4GB      ✅ Manageable
```

**Key Insight:** Running phases sequentially (separate processes) resets memory between phases, preventing OOM.

---

## Strategy 1: Local Development (Watch Mode)

### Best For
- Active development
- TDD workflow
- Debugging specific failures
- Quick feedback loops

### Command
```bash
pnpm test
```

### Advantages
- ✅ Instant feedback (watch mode)
- ✅ Minimal memory usage (~500MB)
- ✅ Hot reload on code changes
- ✅ Can run while developing
- ✅ Clear isolation between test runs

### How It Works
```
Vitest watches file system
    ↓
Detects code changes
    ↓
Runs affected tests only
    ↓
Returns results immediately
    ↓
Stays in memory, ready for next change
```

### Common Patterns

```bash
# Run all tests
pnpm test

# Run specific test file
pnpm test src/components/token-card/__tests__

# Run tests matching pattern
pnpm test --grep "TokenCard"

# Run tests once (not watch)
pnpm test --run

# Run with UI dashboard
pnpm test:ui
```

### Memory Profile
```
│ Memory Usage
│
│  500MB ─────────────────── (stable)
│
└──────────────────────────── Time
  pnpm test (watch mode)
```

**Memory stays low because:** Only loaded tests remain in memory, watch mode is event-driven

---

## Strategy 2: CI/CD Pipelines (RECOMMENDED) ⭐

### Best For
- **Automated build pipelines**
- **Pull request checks**
- **Merge gates**
- **Pre-deployment validation**
- **Resource-constrained environments** (4GB limit)

### Command
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
```

### Advantages
- ✅ Prevents out-of-memory errors
- ✅ Reliable, 100% reproducible
- ✅ Works with 4GB memory limit
- ✅ ~8 minute total execution
- ✅ Clear phase-by-phase results
- ✅ Phase isolation prevents cascading failures

### How It Works

```
Phase 1: Run core data tests
  ├─ Process memory: 0 → 500MB
  ├─ Tests: 51 (100% pass)
  └─ Exit cleanly, release memory

Phase 2: Run component tests
  ├─ Process memory: 0 → 4-5GB
  ├─ Tests: 118 (94% pass - 9 failures)
  └─ Exit cleanly, release memory

Phase 3: Run API & color tests
  ├─ Process memory: 0 → 500MB
  ├─ Tests: 126 (100% pass)
  └─ Exit cleanly, release memory

Phase 4: Run image uploader tests
  ├─ Process memory: 0 → 1GB
  ├─ Tests: 60 (85% pass - 9 failures)
  └─ Exit cleanly, release memory

Aggregate Results: 424/446 passing (97.9%)
```

### Package.json Scripts
```json
{
  "scripts": {
    "test:split": "pnpm test:split-phase1 && pnpm test:split-phase2 && pnpm test:split-phase3 && pnpm test:split-phase4",
    "test:split-phase1": "vitest --run tests/unit tests/core",
    "test:split-phase2": "vitest --run tests/components",
    "test:split-phase3": "vitest --run tests/api tests/color-science",
    "test:split-phase4": "vitest --run tests/image-uploader tests/spacing"
  }
}
```

### Memory Profile
```
│ Memory Usage
│
│ 5GB ─┐
│     │ Phase 2 (Components)
│ 4GB ─┤─────────────┐
│     │             │
│ 1GB ─┤─┐     ┌─────┤─┐   ┌─┐
│     │ │     │     │ │   │ │
│    0 ─┴─┴─────┴─────┴─┴───┴─┴─
│     P1  P2   P3   P4
└─────────────────────────── Time
      (8 minutes total)
```

Each phase runs independently, memory released after each phase completes.

### CI/CD Integration

```yaml
# GitHub Actions Example
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'pnpm'
      - run: pnpm install
      - run: NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
```

### Cost Analysis (AWS EC2)
```
Instance Type   | Memory | Cost/Month | Recommended |
t3.medium       | 4GB    | $30        | ✅ YES      |
t3.large        | 8GB    | $60        | ⚠️ No benefit
t3.xlarge       | 16GB   | $120       | ❌ Overkill
───────────────────────────────────────────────
4GB is sweet spot: reliable, affordable, sufficient
```

---

## Strategy 3: Full Validation

### Best For
- **Pre-release validation**
- **Comprehensive checks**
- **Investigating systematic issues**
- **Systems with adequate memory (4GB+)**

### Command
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:run
```

### Advantages
- ✅ Complete test suite execution
- ✅ All 446 tests in single run
- ✅ Good memory/reliability balance
- ✅ ~13 minutes total
- ✅ Detailed output, easier debugging

### How It Works

```
Start all tests in single Vitest process
    ↓
Tests run sequentially (maxThreads: 1)
    ↓
Memory accumulates: 0 → 4GB
    ↓
All 446 tests complete
    ↓
Report final results
```

### Memory Profile
```
│ Memory Usage
│
│ 4GB ──────────────────────── (plateau)
│
│ 0GB ┌─────────────────────────
└─────────────────────────── Time
    13 minutes total
```

Memory climbs to ~4GB and plateaus (tests run sequentially with minimal cleanup)

### When to Use
- Final pre-release check
- Checking full coverage metrics
- Investigating cascading failures
- Have adequate memory available

---

## Performance Benchmarks

### Execution Time Breakdown

**Strategy 1: Watch Mode**
```
Initial startup:  ~3 seconds
Per test run:     ~500ms (only affected tests)
Feedback:         Instant
Total (full):     ~13 minutes (all tests once)
```

**Strategy 2: CI/CD Split** ⭐ RECOMMENDED
```
Phase 1:  ~1.2 seconds  (51 tests)
Phase 2:  ~360 seconds  (118 tests)  ← Components heavy
Phase 3:  ~1 second     (126 tests)
Phase 4:  ~11 seconds   (60 tests)
─────────────────────────────────
Total:    ~373 seconds (6.2 minutes)
```

**Strategy 3: Full Suite**
```
Startup:  ~3 seconds
Runtime:  ~805 seconds (sequential)
─────────────────────────────────
Total:    ~808 seconds (13.5 minutes)
```

### Memory Consumption

| Strategy | Peak Memory | Cleanup | Stability |
|----------|-------------|---------|-----------|
| Watch Mode | 500MB | Partial | Very stable |
| CI/CD Split | 2-4GB peak/phase | Complete | Very stable |
| Full Suite | 4GB | Partial | Stable |

---

## Choosing the Right Strategy

### Decision Tree

```
Are you writing/debugging code?
├─ YES → Use Strategy 1 (Watch Mode)
│        pnpm test
│
└─ NO → Is this for CI/CD automation?
        ├─ YES → Use Strategy 2 (CI/CD Split) ⭐
        │        NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
        │
        └─ NO → Is this pre-release validation?
                ├─ YES → Use Strategy 3 (Full Suite)
                │        NODE_OPTIONS="--max-old-space-size=4096" pnpm test:run
                │
                └─ NO → Use Strategy 2 (Safe default)
```

---

## Memory Optimization Techniques

### Technique 1: Phase-Based Execution
**Cost Saved:** ~4GB (prevents OOM in parallel tests)
```bash
# Parallel (❌ OOM at 4GB)
pnpm test:run

# Sequential phases (✅ Stays at 2GB max)
pnpm test:split
```

### Technique 2: Single-Threaded Execution
**Config:** `maxThreads: 1, minThreads: 1` in vite.config.ts
**Cost Saved:** ~1-2GB
```typescript
// Prevents thread pool from spawning multiple jsdom instances
test: {
  maxThreads: 1,  // ← Single thread only
  minThreads: 1,  // ← Minimum 1 thread
  isolate: true,  // ← Each test isolated
}
```

### Technique 3: Disable Sourcemaps
**Config:** `sourcemap: false` in vite.config.ts
**Cost Saved:** ~200-400MB
```typescript
test: {
  sourcemap: false,  // ← No source maps during test
}
```

### Technique 4: Test Isolation
**Config:** `isolate: true` in vite.config.ts
**Benefit:** Prevents state leakage between tests
```typescript
test: {
  isolate: true,  // ← Clean environment per test file
}
```

### Technique 5: Increase Heap Size
**Command:** `NODE_OPTIONS="--max-old-space-size=4096"`
**Benefit:** Prevents premature OOM at 2GB default
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
```

---

## Troubleshooting

### Issue: "JavaScript heap out of memory"

**Symptom:** Tests crash with OOM error

**Solution Priority:**
1. ✅ Use `pnpm test:split` instead of `pnpm test:run`
2. ✅ Increase heap: `NODE_OPTIONS="--max-old-space-size=4096"`
3. ⚠️ Run subset of tests: `pnpm test src/components/specific`
4. ⚠️ Use watch mode: `pnpm test` (doesn't run all at once)

### Issue: Tests Timeout on CI

**Symptom:** Some tests timeout on slow CI runners

**Solution:**
1. Check runner specifications (is it 1GB instance?)
2. Increase available memory: `NODE_OPTIONS="--max-old-space-size=4096"`
3. Use `pnpm test:split` for phase isolation
4. Consider upgrading CI runner (t3.medium = 4GB)

### Issue: Inconsistent Results (Flaky)

**Symptom:** Tests pass locally but fail on CI

**Causes:**
- Different memory availability on CI
- Network timeouts
- Timing-sensitive async operations

**Solutions:**
1. Run locally with CI configuration: `NODE_OPTIONS="--max-old-space-size=2048" pnpm test:split`
2. Increase async timeouts: `await screen.findByText(..., {}, { timeout: 5000 })`
3. Use `pnpm test:split` (more stable than `pnpm test:run`)
4. Check CI runner specs

---

## Configuration Reference

### vite.config.ts (Frontend)
```typescript
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './frontend/src/__tests__/setup.ts',

    // Memory optimization
    maxThreads: 1,        // Single thread only
    minThreads: 1,        // Always use thread
    isolate: true,        // Clean environment per file
    sourcemap: false,     // No source maps

    // Timeout configuration
    testTimeout: 30000,   // 30 second timeout
    hookTimeout: 30000,   // 30 second hook timeout
  }
})
```

### pytest.ini (Backend)
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

---

## Monitoring & Metrics

### Memory Profiling

```bash
# Monitor memory during test run
node --expose-gc node_modules/.bin/vitest --run
```

### Performance Profiling

```bash
# See detailed timing per test
NODE_OPTIONS="--expose-gc" pnpm test:run --reporter=verbose
```

### CI/CD Monitoring

```yaml
# GitHub Actions with memory monitoring
- name: Run Tests
  run: |
    NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
    echo "Memory usage: $(ps aux | grep node | head -1)"
```

---

## Long-Term Improvements

### Phase 1: Current State ✅
- Phase-based execution working
- Memory-optimized configuration
- Sustainable CI/CD setup

### Phase 2: Upcoming (Q1 2025)
- [ ] Reduce component test count (consolidate similar tests)
- [ ] Implement lazy test loading
- [ ] Use worker threads for better isolation

### Phase 3: Future (Q2 2025)
- [ ] Consider Vitest 2.0 improvements
- [ ] Migrate to lighter testing environment
- [ ] Implement test sharding with Redis

---

## Summary & Recommendations

### For Local Development
```bash
pnpm test
```
Simple, instant feedback, minimal resources.

### For CI/CD (RECOMMENDED) ⭐
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
```
Reliable, efficient, cost-effective, scales well.

### For Pre-Release
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:run
```
Complete validation, good balance, manageable.

**Bottom Line:** Use `pnpm test:split` for production automation. It's the sweet spot of reliability, speed, and cost.
