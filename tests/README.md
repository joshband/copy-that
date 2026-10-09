# Backend tests (pytest)

| Path | What | Run by CI |
|------|------|-----------|
| `tests/unit/` | Unit tests (incl. `regression/` extraction-accuracy floor) | Yes |
| `tests/integration/` | API / DB integration and `e2e/` pipeline tests | Yes |
| `tests/fixtures/` | Shared test inputs | — |
| `tests/load/locustfile.py` | Locust load test (manual: `locust -f tests/load/locustfile.py`) | No |
| `tests/playwright/` | Stub README only — browser E2E lives in `frontend/tests/playwright/` | No |

`tests/unit` and `tests/integration` are the only pytest homes. Put new backend tests there.

```bash
make verify                          # what CI gates: check + Vitest + pytest unit/integration
make test-quick                      # color/spacing smoke
pytest tests/unit tests/integration  # backend only
```

Tests are hermetic: no network, no paid API calls, no reliance on a developer `.env` (the root `tests/conftest.py` strips it). See [TESTING_GUIDE.md](../docs/testing/TESTING_GUIDE.md).
