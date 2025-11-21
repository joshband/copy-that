# Alembic Migrations

## Author
```bash
alembic revision --autogenerate -m "message"
```

## Apply
```bash
alembic upgrade head
```

## Rollback (use cautiously)
```bash
alembic downgrade -1
```

Prereq: configure DB URL in `.env` and ensure models are imported before `Base.metadata.create_all` in tests (see `tests/conftest.py`).
