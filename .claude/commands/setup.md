Set up the copy-that development environment and validate all CI checks pass.

## Setup

1. **Install locked dependencies and git hooks** (needs Python 3.12+, `uv`, Node 20+, `pnpm`)
   ```bash
   make install
   ```
   This runs `uv sync --frozen --extra dev` (creates `.venv`), `pnpm install --frozen-lockfile`,
   and installs the pre-commit + pre-push hooks. Same versions as CI.

2. **Install the Playwright browser** (for E2E only)
   ```bash
   pnpm exec playwright install chromium
   ```

3. **Environment**
   ```bash
   cp .env.example .env   # never read or print an existing .env
   make db-bootstrap      # or: make db-bootstrap-sqlite (no Docker)
   ```

4. **Run the CI gates**
   - Fast: `make check` — mypy + ruff + format + tsc + eslint (~1 min)
   - Full: `make verify` — check + full Vitest + pytest `tests/unit` `tests/integration` (what CI gates)
   - E2E: `pnpm test:e2e:mvp` — Playwright MVP pack (mocked)

5. **Fix any failures** encountered during the checks

6. **Report final status** with summary of:
   - Python / uv versions
   - Node / pnpm versions
   - Number of tests passed
   - Any issues found and fixed

## Available Test Commands

| Command | Description |
|---------|-------------|
| `make test-quick` | Backend color/spacing smoke |
| `make test` | Full pytest run over `tests/` |
| `make coverage` / `make coverage-quick` | Coverage report (all / unit only) |
| `make test-watch` | Re-run unit tests on save |
| `pnpm test:all` | Full Vitest suite |
| `pnpm test:e2e` | All Playwright specs (`frontend/tests/playwright/`) |
| `pnpm test:e2e:mvp` | Playwright MVP pack (mocked) |

Load tests: `locust -f tests/load/locustfile.py` (manual, not in CI).

## Development Guidelines

### Test-Driven Development (TDD)

**Always follow TDD when implementing new features:**

1. **Write tests first** - Define expected behavior before implementation
2. **Run tests to see them fail** - Confirm tests are correctly written
3. **Implement the feature** - Write minimal code to pass tests
4. **Refactor** - Clean up while keeping tests green

**TDD applies to:**
- New components (write component tests first)
- API integrations (write schema validation tests first)
- Utility functions (write unit tests first)
- Bug fixes (write regression test first)

**Frontend testing:**
```bash
pnpm test:all
```

**Backend testing:**
```bash
.venv/bin/pytest tests/unit tests/integration -q
```

### Defensive Patterns

- Use TypeScript strict mode and `strictNullChecks`
- Validate API responses with `zod` schemas
- Make array props optional with defaults: `{ colors = [] }`
- Handle undefined/null gracefully in components
