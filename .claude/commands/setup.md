Set up the copy-that development environment and validate all CI checks pass.

## Quick Setup (Recommended)

Run the automated setup script:
```bash
./scripts/setup-dev.sh
```

This installs dependencies, sets up pre-commit hooks, and validates the environment.

## Manual Steps

1. **Install dependencies and pre-commit hooks**
   ```bash
   make install
   ```
   Or with uv:
   ```bash
   uv pip install -e ".[dev]"
   pre-commit install --hook-type pre-commit --hook-type pre-push
   ```

2. **Install Playwright browsers for UI testing**
   ```bash
   playwright install chromium --with-deps
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend && npm install && cd ..
   ```

4. **Run CI checks** (tiered approach):
   - Light tier (fast): `make ci-light`
   - Medium tier (full): `make ci-medium`
   - Heavy tier (all): `make ci-heavy`

   Or individual checks:
   - Linting: `make lint`
   - Format check: `make format-check`
   - Type checking: `make type-check`
   - Fast unit tests: `make test-fast`
   - All tests: `make test-all`

5. **Fix any failures** encountered during the checks

6. **Report final status** with summary of:
   - Python/pip versions
   - Node/npm versions
   - Number of tests passed
   - Any issues found and fixed

## Available Test Commands

| Command | Description |
|---------|-------------|
| `make test` | Fast unit tests (~30s) |
| `make test-unit` | Full unit tests |
| `make test-int` | Integration tests |
| `make test-e2e` | E2E tests with Playwright |
| `make test-visual` | Visual regression tests |
| `make test-a11y` | Accessibility tests |
| `make test-api` | API contract tests |
| `make test-load` | Load tests with Locust |
| `make test-cov` | Tests with coverage report |

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
cd frontend && npm test
```

**Backend testing:**
```bash
.venv/bin/pytest tests/ -q
```

### Defensive Patterns

- Use TypeScript strict mode and `strictNullChecks`
- Validate API responses with `zod` schemas
- Make array props optional with defaults: `{ colors = [] }`
- Handle undefined/null gracefully in components
