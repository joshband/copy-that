# Fast Development Workflow - Stop Wasting Time on CI Failures!

**Problem:** Committing → Pushing → Waiting 10+ minutes → CI fails on mypy/ruff/tests
**Solution:** Catch everything locally in SECONDS, not minutes

---

## 🚀 Your New Fast Workflow

### Every Code Change (30 seconds)

```bash
# Before commit - Fast validation
make check          # mypy + ruff + typecheck (30 sec)

# OR use the pre-push hook (automatic)
git push            # Hook runs validation automatically
```

### Before Major Push (2-3 minutes)

```bash
# Run quick smoke tests
make test-quick     # Critical tests only (2-3 min)

# OR full local CI
make ci-local       # Everything CI runs (5-10 min)
```

### Generate Coverage Locally (1 minute)

```bash
# Run tests with coverage
make coverage       # Generates HTML report

# View report
open htmlcov/index.html
```

---

## ⚡ Fast Commands (Added to Makefile)

### Validation Commands

```bash
make check          # ⚡ 30 sec - mypy + ruff + typecheck
make quick          # Same as make check
make ci-local       # 🕐 5-10 min - Full CI locally
```

### Testing Commands

```bash
make test-quick     # ⚡ 2-3 min - Smoke tests only
make test-unit      # 🕐 5 min - Unit tests
make test           # 🕐 10-15 min - Full suite
make test-watch     # 👀 Continuous - TDD mode
make coverage       # 📊 1 min - Generate coverage report
```

### Development Commands

```bash
make dev            # Start Docker Compose
make stop           # Stop services
make logs           # View logs
make restart        # Restart services
```

### Database Commands

```bash
make db-migrate     # Run migrations
make db-rollback    # Rollback last migration
make db-reset       # ⚠️  Reset database (drops all data)
```

---

## 🎯 Recommended Workflow

### Feature Development (Fast Iteration)

```bash
# 1. Start development environment
make dev

# 2. Code your feature
#    Frontend: http://localhost:3000
#    Backend: http://localhost:8000 (auto reload)

# 3. Before commit - Fast validation (30 sec)
make check

# 4. Commit
git add .
git commit -m "feat: Your feature"

# 5. Before push - Quick tests (2-3 min)
make test-quick

# 6. Push (pre-push hook validates automatically)
git push

# TOTAL TIME: ~3-4 minutes of local validation
# vs 10-15 minutes waiting for CI to fail!
```

### Bug Fix (Ultra Fast)

```bash
# 1. Make fix

# 2. Fast validation
make check              # 30 sec

# 3. Push
git push                # Pre-push hook validates automatically

# TOTAL TIME: 30 seconds!
```

### Major Feature (Full Validation)

```bash
# 1. Develop feature

# 2. Run full local CI
make ci-local           # 5-10 min (everything CI runs)

# 3. Generate coverage report
make coverage

# 4. Review coverage
open htmlcov/index.html

# 5. Push with confidence
git push                # Should pass CI first time!

# TOTAL TIME: 5-10 min locally (one time)
# vs multiple 10+ min CI cycles!
```

---

## 🔍 Pre-Push Hook (Automatic Validation)

**What it does:**
- Runs on every `git push`
- Validates: mypy, ruff, pnpm typecheck
- Takes: ~30 seconds
- Blocks push if validation fails

**To skip (emergency only):**
```bash
git push --no-verify
```

**To test hook without pushing:**
```bash
.git/hooks/pre-push
```

---

## 📊 Local Coverage Reports

### Generate Coverage

```bash
# Run tests with coverage
make coverage

# This creates:
# - coverage.xml (for Codecov)
# - htmlcov/ directory (HTML report)
```

### View Coverage Locally

```bash
# Open in browser
open htmlcov/index.html

# Or command line
source .venv/bin/activate
coverage report
```

### Coverage vs Codecov

**Local Coverage (htmlcov/):**
- ✅ Instant feedback (1 minute)
- ✅ Visual HTML report
- ✅ Shows uncovered lines
- ✅ Works offline
- ✅ Free, no limits

**Codecov (cloud service):**
- ✅ Tracks coverage over time
- ✅ PR comments with diff coverage
- ✅ Coverage badges
- ✅ Team dashboards
- ⏱️ Only updates after CI runs

**Best Practice:** Use local coverage during development, Codecov for tracking trends.

---

## 🏃 Speed Optimizations

### What Makes This Fast

**1. Pre-Push Hook (30 seconds)**
- Only runs static checks (no tests)
- Uses cached mypy results
- Parallel execution where possible

**2. make check (30 seconds)**
- Skips tests (too slow)
- Only validates code quality
- Same checks CI will run

**3. make test-quick (2-3 minutes)**
- Runs subset of critical tests
- Uses `-x` flag (stop on first failure)
- `--maxfail=5` (stop after 5 failures)
- Only tests color/spacing (core features)

**4. make ci-local (5-10 minutes)**
- Full validation (everything CI runs)
- But runs locally (no network latency)
- Uses local Docker cache
- Parallel test execution

---

## 🎯 Time Savings Comparison

### Old Workflow (Slow)
```
Code → Commit → Push → Wait 2 min → CI starts
  → Wait 10 min → CI fails on mypy
  → Fix → Push → Wait 2 min → CI starts
  → Wait 10 min → CI fails on tests
  → Fix → Push → Wait 2 min → CI starts
  → Wait 10 min → CI passes ✅

TOTAL: ~36 minutes, 3 CI runs
```

### New Workflow (Fast)
```
Code → make check (30 sec) → Fix if needed
  → make test-quick (2-3 min) → Fix if needed
  → git push (pre-push hook: 30 sec)
  → Wait 2 min → CI starts
  → Wait 10 min → CI passes ✅ (first time!)

TOTAL: ~15 minutes, 1 CI run
SAVINGS: 21 minutes (58% faster!)
```

---

## 📋 Complete Development Workflow Guide

### Morning Routine (Start of Day)

```bash
# 1. Pull latest
git pull

# 2. Start services
make dev

# 3. Run migrations (if any)
make db-migrate

# 4. Verify everything works
make check
```

### Feature Development Loop

```bash
# Repeat this cycle:

# 1. Code your feature
#    (servers auto-reload)

# 2. Fast validation
make check                    # Every 15-30 min

# 3. Quick tests
make test-quick               # When feature complete

# 4. Commit
git add .
git commit -m "feat: ..."

# 5. Push
git push                      # Hook validates automatically
```

### Code Review / PR Ready

```bash
# Before creating PR:

# 1. Full local CI
make ci-local

# 2. Generate coverage
make coverage
open htmlcov/index.html

# 3. Check coverage threshold
coverage report --fail-under=80

# 4. Push
git push

# 5. Create PR
gh pr create
```

### Debugging CI Failures (If They Happen)

```bash
# 1. Check which job failed
gh run list --limit 1

# 2. View failure logs
gh run view --log-failed

# 3. Reproduce locally
make ci-local

# 4. Fix and validate
make check
make test

# 5. Push
git push
```

---

## 🛠️ Enhanced Makefile Commands

### Added Commands

```makefile
coverage:          # Generate coverage report (HTML + XML)
test-watch:        # TDD mode - auto-run tests on file changes
test-failed:       # Re-run only failed tests
ruff-fix:          # Auto-fix linting issues
ci-watch:          # Monitor CI status
clean:             # Clean build artifacts
clean-docker:      # Remove Docker containers/images
```

### Usage Examples

```bash
# Auto-fix linting
make ruff-fix

# Watch tests while coding
make test-watch

# Re-run only failed tests
make test-failed

# Watch CI progress
make ci-watch
```

---

## 📊 Coverage Reports Integration

### Local Coverage Generation

Add to Makefile:

```makefile
coverage: ## Generate coverage report (local, fast)
	@echo "📊 Generating coverage report..."
	@source .venv/bin/activate && pytest tests/ \
		--cov=src/copy_that \
		--cov-report=html \
		--cov-report=xml \
		--cov-report=term
	@echo ""
	@echo "✅ Coverage report generated!"
	@echo "   HTML: open htmlcov/index.html"
	@echo "   XML:  coverage.xml (for Codecov)"

coverage-quick: ## Quick coverage (unit tests only)
	@source .venv/bin/activate && pytest tests/unit \
		--cov=src/copy_that \
		--cov-report=term

coverage-report: ## Show coverage report (terminal)
	@source .venv/bin/activate && coverage report
```

### Codecov Integration (Automatic in CI)

**Already configured in ci.yml:**
- Lines 149-156: Unit test coverage upload
- Lines 164-171: Integration test coverage upload

**How it works:**
1. CI runs tests with `--cov-report=xml`
2. Uploads `coverage-unit.xml` to Codecov
3. Codecov updates badge automatically
4. PR comments show coverage diff

**To view Codecov dashboard:**
- https://codecov.io/gh/joshband/copy-that

---

## 🎯 Streamlined Code → Cloud Run Flow

### Development → Production Pipeline

```
┌─────────────────────────────────────────────────────┐
│ LOCAL DEVELOPMENT (Instant Feedback)               │
├─────────────────────────────────────────────────────┤
│ 1. Code in IDE (hot reload)                         │
│ 2. make check (30 sec) - Catch issues immediately   │
│ 3. make test-quick (2-3 min) - Smoke tests          │
│ 4. git commit                                        │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ PRE-PUSH VALIDATION (30 seconds)                    │
├─────────────────────────────────────────────────────┤
│ git push triggers:                                   │
│ • mypy type check                                    │
│ • ruff linter                                        │
│ • pnpm typecheck                                     │
│ ❌ Blocks push if any fail                          │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ GITHUB ACTIONS CI (10-15 minutes)                   │
├─────────────────────────────────────────────────────┤
│ • Security scan                                      │
│ • Lint + Type check (should pass - already validated)│
│ • Unit tests + Integration tests                    │
│ • Docker build                                       │
│ • Upload coverage to Codecov                        │
│ ✅ Should pass first time!                          │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ BUILD WORKFLOW (5 minutes)                          │
├─────────────────────────────────────────────────────┤
│ • Build Docker image                                 │
│ • Push to GCP Artifact Registry                     │
│ • Tag with commit SHA                                │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ DEPLOY WORKFLOW (2-3 minutes)                       │
├─────────────────────────────────────────────────────┤
│ • Deploy to Cloud Run (staging or production)       │
│ • Run database migrations                            │
│ • Smoke tests (health check)                        │
│ ✅ Live on Cloud Run!                               │
└─────────────────────────────────────────────────────┘

TOTAL TIME: ~20-25 minutes (first-time success!)
vs ~36+ minutes with multiple CI failures
```

---

## 🏎️ Ultra-Fast Iteration Mode (For Active Development)

When actively developing a feature:

```bash
# Terminal 1: Services
make dev && make logs

# Terminal 2: Tests in watch mode
make test-watch

# Terminal 3: Code
vim src/...

# Workflow:
# 1. Edit code → Save
# 2. Tests auto-run (2-5 sec)
# 3. See results immediately
# 4. Fix → Save → Repeat

# When done:
make check          # 30 sec validation
git commit
git push            # Pre-push hook validates (30 sec)
```

**Result:** Instant feedback, no waiting!

---

## 🎯 Pre-Push Hook Features

**What it checks (in order):**
1. ✅ mypy type checking (~10 sec)
2. ✅ ruff linting (~5 sec)
3. ✅ ruff formatting (~5 sec)
4. ✅ pnpm typecheck (~10 sec)
5. ⏭️ Alembic migrations (quick check, ~2 sec)

**What it DOESN'T check (too slow):**
- ❌ Full test suite (run with `make test-quick` instead)
- ❌ Docker builds (run with `make build` if needed)
- ❌ Integration tests (CI handles these)

**Total time:** ~30 seconds (vs 10+ minutes of CI)

---

## 📊 Coverage Workflow

### Local Coverage (Fast Development)

```bash
# Run tests with coverage
make coverage

# View HTML report (interactive)
open htmlcov/index.html

# Check specific file
coverage report src/copy_that/extractors/color/extractor.py

# Check if meeting threshold
coverage report --fail-under=80
```

**Benefits:**
- ✅ Instant feedback
- ✅ See exact uncovered lines
- ✅ Identify gaps before PR

### Codecov (CI Integration)

**Automatic on every push:**
- CI runs tests with coverage
- Uploads to codecov.io
- Badge updates automatically
- PR comments show diff coverage

**View Codecov:**
- Dashboard: https://codecov.io/gh/joshband/copy-that
- Badge: Shows in README.md

**Best Practice:**
- Use local coverage while developing
- Use Codecov to track trends over time

---

## 🚦 Optimization Tips

### 1. Use Watch Mode for TDD

```bash
# In one terminal
make test-watch

# Edit code in another terminal
# Tests auto-run on save
# Immediate feedback!
```

### 2. Run Only Changed Tests

```bash
# After fixing a test
make test-failed

# Only runs tests that failed last time
# Much faster than full suite
```

### 3. Use pytest-xdist for Parallel Tests

Add to Makefile:

```bash
test-parallel: ## Run tests in parallel (4x faster)
	@source .venv/bin/activate && pytest tests/ -n auto
```

### 4. Cache mypy Results

mypy already caches results in `.mypy_cache/`
- First run: ~10 seconds
- Subsequent runs: ~2-5 seconds (only checks changed files)

### 5. Skip Slow Tests Locally

```bash
# Mark slow tests with @pytest.mark.slow
# Then run:
pytest -m "not slow"  # Skip slow tests
```

---

## 🎯 Time Savings Summary

| Task | Old Way | New Way | Savings |
|------|---------|---------|---------|
| Type check | Wait for CI (12 min) | make check (30 sec) | 11.5 min |
| Lint errors | Wait for CI (12 min) | make check (30 sec) | 11.5 min |
| Test failures | Wait for CI (12 min) | make test-quick (3 min) | 9 min |
| Coverage report | Wait for CI (12 min) | make coverage (1 min) | 11 min |
| **Total per iteration** | **12-15 min** | **30 sec - 3 min** | **~10 min** |

**Per day (5 iterations):**
- Old: ~60-75 minutes waiting for CI
- New: ~2.5-15 minutes local validation
- **Savings: ~45-60 minutes per day!**

---

## 🔧 Setup (One-Time)

### 1. Install Pre-Push Hook

```bash
# Already done! Hook created at .git/hooks/pre-push
# Test it:
.git/hooks/pre-push
```

### 2. Install pytest-watch (Optional)

```bash
source .venv/bin/activate
pip install pytest-watch
```

### 3. Configure Coverage Thresholds

Add to `pyproject.toml`:

```toml
[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = false

[tool.coverage.run]
source = ["src/copy_that"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__pycache__/*",
]
```

---

## 🎯 Workflow Decision Tree

```
Starting to code?
├─ Just exploring → Code directly, no validation yet
├─ Small fix → make check (30 sec) → push
├─ Feature development → make check + make test-quick (3 min) → push
└─ Major feature → make ci-local (10 min) → make coverage → review → push
```

**Before every push:**
```
git push triggers pre-push hook automatically:
├─ mypy passes? ✅ → Continue
├─ ruff passes? ✅ → Continue
├─ typecheck passes? ✅ → Continue
└─ All pass → Push proceeds → CI likely succeeds! 🎉
```

---

## 🚀 Quick Reference Card

Print this and keep it visible!

```
═══════════════════════════════════════════════════
        FAST DEVELOPMENT WORKFLOW
═══════════════════════════════════════════════════

BEFORE EVERY COMMIT:
  make check              (30 sec)

BEFORE EVERY PUSH:
  make test-quick         (2-3 min)
  # OR let pre-push hook handle it

BEFORE CREATING PR:
  make ci-local           (5-10 min)
  make coverage           (1 min)
  open htmlcov/index.html

WHILE CODING (TDD):
  make test-watch         (continuous)

VIEW LOCAL COVERAGE:
  make coverage
  open htmlcov/index.html

FIX LINTING:
  make ruff-fix           (auto-fix)

═══════════════════════════════════════════════════
         STOP WAITING FOR CI TO FAIL!
        CATCH ISSUES LOCALLY IN SECONDS
═══════════════════════════════════════════════════
```

---

## 🎯 Next Steps

1. **Test the system:**
   ```bash
   make check          # Should pass in 30 sec
   ```

2. **Try the pre-push hook:**
   ```bash
   git push --dry-run  # Test without actually pushing
   ```

3. **Generate your first local coverage report:**
   ```bash
   make coverage
   open htmlcov/index.html
   ```

4. **Start using the fast workflow:**
   - Code → `make check` → commit → `make test-quick` → push
   - Total: ~3 minutes vs waiting 12+ minutes for CI!

---

**Your new workflow is 10x faster!** 🚀

No more waiting for CI to tell you about issues you could have caught in 30 seconds locally!
