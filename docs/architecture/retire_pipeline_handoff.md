# Legacy Pipeline Retirement – Handoff

Status: WIP on branch `chore/retire-legacy-pipeline`

## What’s done
- Added deprecation notice in `src/copy_that/pipeline/__init__.py` (emits `DeprecationWarning`).
- Documented the retirement plan in `docs/architecture/legacy_pipeline_retirement.md`.
- README now notes the legacy multi-agent pipeline is deprecated and points to the new token-graph flow.

## Open work for Issue #70
1) **Legacy imports to handle** (from `rg 'copy_that\\.pipeline'`):
   - Integration/tests: `tests/token_smoke_test.py`, `tests/integration/test_pipeline_integration.py`, all suites under `tests/unit/pipeline/**`, plus `tests/unit/test_color_pipeline_comprehensive.py`, `tests/unit/test_*` files referencing orchestrator/validation/aggregation/generator.
   - Runtime (inside pipeline package): validation, extraction, orchestrator, preprocessing, aggregation, generator modules import each other.
   - Check for any API/CLI usage outside `src/copy_that/pipeline/**` (none spotted yet via `rg`, but double-check any scripts/CLI).

2) **Next steps to execute**
   - Step 1: Mark legacy pipeline tests as `xfail`/`skip` or rewrite the smoke test to import the new panel pipeline (`panel_to_tokens`). Candidates: all `tests/unit/pipeline/**`, `tests/integration/test_pipeline_integration.py`, `tests/token_smoke_test.py`.
   - Step 2: Confirm no non-test call sites depend on `copy_that.pipeline.*`. If none, prepare to delete `src/copy_that/pipeline/**` after tests are skipped/migrated.
   - Step 3: If any API/CLI route still relies on the legacy pipeline, add a thin adapter that calls the token-graph flow (`TokenRepository` + `tokens_to_w3c`, `panel_to_tokens`) and then remove the old implementation.
   - Step 4: Remove legacy modules and fixtures once all imports are gone; update docs to reference only the token-graph architecture.

3) **Outstanding local changes**
   - Unrelated: `docker-compose.yml` (modified) and auth test rename (deleted `tests/integration/test_authorization.py`, added `tests/integration/test_authorization_integration.py`) are still unstaged—leave untouched unless needed.

## Branches/commits
- Current branch: `chore/retire-legacy-pipeline`
- Latest commit: `3703843 chore: mark legacy pipeline deprecated and document retirement plan`

## Quick commands to resume
- `git switch chore/retire-legacy-pipeline`
- Inspect imports: `rg 'copy_that\\.pipeline' src tests`
- Start skips: add `pytest.mark.skip(reason="legacy pipeline deprecated")` to legacy test modules, or rewrite `tests/token_smoke_test.py` to import `pipeline/panel_to_tokens`.
- If deleting legacy code: remove `src/copy_that/pipeline/**` after confirming no remaining imports.
