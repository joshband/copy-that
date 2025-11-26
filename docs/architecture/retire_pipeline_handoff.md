# Legacy Pipeline Retirement – Handoff

Status: WIP on branch `chore/retire-legacy-pipeline`

## What’s done
- Added deprecation notice (now removed with the package).
- Documented the retirement plan in `docs/architecture/legacy_pipeline_retirement.md`.
- README notes the legacy multi-agent pipeline is deprecated and points to the new token-graph flow.
- Deleted `src/copy_that/pipeline/**` and all legacy pipeline test suites; skipped legacy tests in `tests/conftest.py`.
- Stubbed `scripts/generate_figma_tokens.py` to exit early (legacy dependency).

## Open work for Issue #70
1) **Legacy imports to handle**
   - Remaining: docs and `scripts/generate_figma_tokens.py` now stubbed to exit (relied on legacy pipeline).
   - Runtime: no `copy_that.pipeline.*` usages outside the deleted package.

2) **Next steps to execute**
   - Update any docs referencing the legacy pipeline to point to the token-graph flow (optional cleanup).
   - Replace the figma generator script with a token-graph-based export or remove it if unused.
   - Run a quick `rg 'copy_that\\.pipeline'` to confirm no new references have appeared before closing Issue #70.

3) **Outstanding local changes**
   - Unrelated: `docker-compose.yml` (modified) and auth test rename (deleted `tests/integration/test_authorization.py`, added `tests/integration/test_authorization_integration.py`) are still unstaged—leave untouched unless needed.

## Branches/commits
- Current branch: `chore/retire-legacy-pipeline`
- Latest commits: `042ff6e` (skip legacy tests, add handoff), `3703843` (deprecation/doc), deletion commit pending.

## Quick commands to resume
- `git switch chore/retire-legacy-pipeline`
- Verify no references: `rg 'copy_that\\.pipeline'`
- Decide fate of `scripts/generate_figma_tokens.py` (rewrite using token graph or remove)
- Clean up docs references if desired, then close Issue #70.
