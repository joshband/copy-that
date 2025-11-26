# Legacy Pipeline Retirement Plan

The old multi-agent pipeline under `src/copy_that/pipeline/**` (agents/orchestrators, etc.) is now superseded by the token graph flow (`core.tokens.*`, `cv_pipeline.*`, `layout.*`, `typography.*`, `pipeline/panel_to_tokens.py`). This doc tracks deprecation and removal.

## Current State
- Legacy modules under `src/copy_that/pipeline/**` have been removed.
- New token graph + panel pipeline is merged and used for CV-first flows, with W3C exports via `tokens_to_w3c`.

## Migration Tasks
1. **Usage inventory** – locate remaining imports of `copy_that.pipeline.*` in API/CLI/tests; replace with token-graph utilities where feasible.
2. **API/CLI swaps** – wire any live endpoints or commands to the token graph (e.g., use `panel_to_tokens` or direct `TokenRepository` helpers).
3. **Test cleanup** – drop or rewrite legacy pipeline tests once call sites move to the new path. (Legacy tests now skipped; source removed.)
4. **Remove legacy code** – ✅ done. Update docs to point only to the token graph architecture.

## Guidance
- Prefer `TokenRepository` + `tokens_to_w3c` as the serialization surface.
- For CV/image inputs, share preprocessing via `cv_pipeline.preprocess` and primitives.
- For layout/typography, reuse `layout.*` + `typography.recommender`.

Once no runtime code imports the legacy pipeline, we can safely remove it and the associated fixtures.
