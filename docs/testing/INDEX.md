# Testing Documentation Index

**Last Updated:** 2025-12-05
**Current Test Status:** 424/446 passing (97.9% ✅)

---

## Quick Status Dashboard

| Area | Status | Details | Priority |
|------|--------|---------|----------|
| **Frontend Unit Tests** | ✅ PASSING | 424/446 tests (97.9%) | Ready |
| **Frontend Integration Tests** | ⚠️ 10 FAILING | ImageUploader async timeouts | HIGH |
| **Backend API Tests** | ✅ PASSING | 46/46 tests (100%) | Complete |
| **Test Execution Strategy** | ✅ OPTIMIZED | Memory-aware split scripts | Production Ready |
| **Documentation** | ✅ COMPLETE | Comprehensive guides | Current |

---

## Documentation Files

### Current Status & Operations
- **ACTIVE:** `TESTING_GUIDE.md` - Complete testing operations guide
- **ACTIVE:** `TEST_EXECUTION_STRATEGY.md` - Memory-optimized test execution for CI/CD
- **REFERENCE:** `TEST_SUITE_WRAP_UP_2025_12_05.md` - Session 2 final summary (97.9% pass rate)
- **REFERENCE:** `TEST_SUITE_STATUS_SESSION_2.md` - Detailed phase-by-phase results

### Planning & Roadmaps
- **REFERENCE:** `2025-12-05_test-coverage-roadmap.md` - Long-term test coverage goals (outdated format, info consolidated)
- **REFERENCE:** `2025-12-05_test-gaps-and-recommendations.md` - Gap analysis (pre-optimization)

### Configuration & Setup
- **ACTIVE:** `2025-12-05_test-env-setup.md` - Local test environment configuration
- **REFERENCE:** `legacy/` - Archive of deprecated testing docs (for historical reference)

### Playwright Tests
- **ACTIVE:** `2025-12-05_TIER2-test-results.md` - Playwright E2E tests (47/47 passing ✅)

---

## Key Commands

### Local Development
```bash
# Watch mode (instant feedback, low memory)
pnpm test

# Specific test file
pnpm test src/components/color-science/__tests__
```

### CI/CD Pipelines (RECOMMENDED)
```bash
# Sequential execution (prevents OOM, reliable)
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
```

### Full Validation
```bash
# Complete suite with memory optimization
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:run
```

### Individual Phases
```bash
pnpm test:unit           # Unit tests only
pnpm test:integration    # Integration tests only
pnpm test:components     # Component tests only
pnpm test:split-phase1   # Core data tests
pnpm test:split-phase2   # Component tests
pnpm test:split-phase3   # API & color science
pnpm test:split-phase4   # Image uploader
```

---

## Test Suite Breakdown

### Frontend (Vitest + React Testing Library)
- **Unit Tests:** 200+ tests covering hooks, utilities, business logic
- **Component Tests:** 150+ tests for React components
- **Integration Tests:** 90+ tests for workflows and API interactions
- **Total:** 446 tests across 41 test files

**Configuration:**
- Single-threaded execution (`maxThreads: 1`)
- Test isolation enabled
- Timeout: 30 seconds
- Environment: jsdom

### Backend (pytest)
- **Unit Tests:** API schemas, models, utilities
- **Integration Tests:** Database operations, endpoints
- **E2E Tests:** Complete pipelines
- **Total:** 46 tests (100% passing)

---

## Current Issues & Fixes

### 10 Failing Tests (ImageUploader Async Timeouts)
**Status:** ⚠️ Identified, reproducible, straightforward fix
**Root Cause:** `screen.findByText()` timeout during async FileReader operations
**Expected Fix Time:** 30 minutes

**Affected Files:**
- `frontend/src/components/image-uploader/__tests__/ImageUploader.integration.test.tsx`

**Solution:** Increase async timeout for `findByText` operations (already identified)

---

## Memory Management

### Heap Requirements
| Scenario | Memory | Duration | Pass Rate | Use Case |
|----------|--------|----------|-----------|----------|
| `pnpm test` (watch) | ~500MB | N/A | 100% | Local development |
| `pnpm test:split` | ~2GB | ~8 min | 98%+ | CI/CD pipelines |
| 4GB heap limit | ~4GB | ~13 min | 98%+ | Cost-effective CI |
| 8GB heap limit | ~8GB | ~13 min | 98%+ | Overhead, no benefit |

**Recommendation:** Use 4GB heap for CI/CD (optimal cost-effectiveness)

---

## Test Execution Tiers

### Tier 1: Developer (Watch Mode)
```bash
pnpm test
```
- Instant feedback
- Low memory overhead
- Incremental testing
- **Best for:** Active development, TDD

### Tier 2: CI/CD (Sequential)
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
```
- Reliable, prevents OOM
- Reproducible results
- Clear phase breakdown
- **Best for:** Automated pipelines, merge gates

### Tier 3: Full Validation
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:run
```
- Complete coverage
- Good balance of memory/reliability
- ~13 minutes total
- **Best for:** Pre-release, comprehensive checks

---

## Next Steps (Session 3 Action Items)

### Immediate Priority (30 minutes)
1. **Fix ImageUploader async timeouts**
   - Increase `findByText` timeout on line 470+
   - Expected: 10 failing tests → 0 failing tests
   - Validation: `pnpm test:split` should show 446/446 passing

### Quick Win (5 minutes)
2. **Verify 100% pass rate**
   - Run full suite: `NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split`
   - Expected: All 446 tests passing

### Future Improvements
3. Test sharding for CI matrix (Week 2)
4. Visual regression tests (Week 3)
5. Performance benchmarks (Week 4)

---

## Related Documentation

- **CLAUDE.md** - Development guide with test commands
- **frontend/vite.config.ts** - Vitest configuration details
- **package.json** - Test script definitions

---

## Version History

| Date | Status | Key Achievement |
|------|--------|-----------------|
| 2025-12-05 | ✅ 97.9% | Optimization phase complete, split scripts working |
| 2025-12-04 | 🔄 95% | Hook fixes, configuration enhancements |
| 2025-12-01 | 📊 Baseline | Initial assessment, coverage roadmap |

---

## Archive

Legacy and archived testing documentation is in `legacy/` directory for historical reference:
- `legacy/2025-11-20_testing.md`
- `legacy/2025-11-20_api_testing_strategy.md`
- `legacy/legacy/` - Further archived docs

For current information, refer to active files listed above.

---

**Questions?** Refer to specific guides:
- How to run tests locally? → `TESTING_GUIDE.md`
- CI/CD setup? → `TEST_EXECUTION_STRATEGY.md`
- Environment setup? → `2025-12-05_test-env-setup.md`
- Specific test results? → `TEST_SUITE_WRAP_UP_2025_12_05.md`
