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
