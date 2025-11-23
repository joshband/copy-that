Set up the copy-that development environment and validate all CI checks pass.

## Steps

1. **Create Python 3.12 virtual environment**
   ```bash
   /usr/bin/python3.12 -m venv .venv
   ```

2. **Install all Python dependencies** (including dev extras)
   ```bash
   .venv/bin/pip install -e ".[dev]"
   ```

3. **Install Playwright and browsers for UI testing**
   ```bash
   .venv/bin/pip install pytest-playwright
   .venv/bin/python -m playwright install chromium
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend && npm install && cd ..
   ```

5. **Run all CI checks**:
   - Linting: `.venv/bin/ruff check . && .venv/bin/ruff format --check .`
   - Type checking: `.venv/bin/mypy src/`
   - Unit tests: `.venv/bin/pytest tests/unit/ -q`
   - Integration tests: `.venv/bin/pytest tests/integration/ -q`

6. **Fix any failures** encountered during the checks

7. **Report final status** with summary of:
   - Python/pip versions
   - Node/npm versions
   - Number of tests passed
   - Any issues found and fixed

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
