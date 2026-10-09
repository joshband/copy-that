# Copy That — Product roadmap

**Status:** Active planning source of truth · **Updated:** 2026-10-09

Screenshot → reliable design tokens → W3C / CSS / React / Tailwind / Guide Pack export.
Mood and Lighting are opt-in; neither runs during upload extraction. Navigation values
live in [featureFlags.ts](../../frontend/src/config/featureFlags.ts).

## Current product

The upload path extracts color, spacing, typography, and shadow tokens, derives shape
and additional DTCG types, persists project tokens, and exports the token graph.
Derived presets and recommendations must remain distinguishable from measurements.
Export coverage does not prove extraction accuracy for every DTCG family.

Mood uses a separate explicit generation action. Lighting calls geometry on demand.
Upload must never invoke geometry, FastSAM, UIED, Marigold, or depth models.
Sessions, batch, and multi-extract are API-only and independently configurable;
jobs remains available for Mood polling. See [architecture](../architecture/CURRENT_ARCHITECTURE_STATE.md)
and [runtime controls](../configuration/ENVIRONMENT_VARIABLES.md#api--runtime).

## Next cycle: extraction precision

Freeze new Mood features and platform expansion while improving the extract/export
spine. Authentication and compatibility maintenance remain prerequisites, not a new
Mood feature cycle.

1. Diagnose extra amber tints in the hermetic color evaluation. Preserve recall while
   removing unsupported palette entries; use [the scored evaluation](../../tests/unit/regression/test_extraction_accuracy.py)
   as the baseline rather than copying its thresholds into documentation.
2. Expand the labelled fixture set to light/dark UI, antialiasing, gradients, and
   subtle shadows. Record provenance, expected tokens, and precision/recall by family.
   Keep paid providers outside automated tests.
3. Validate resulting tokens through persistence and export, including truthful
   confidence and measured/derived/fallback labels. Mocked browser checks prove UI
   behavior; image evaluation and explicit live runs provide separate evidence.
4. Continue draining legacy `application/` modules only in bounded migrations that
   preserve behavior. Claude color and spacing utilities have canonical homes;
   other extractor/model duplicates remain.

Acceptance requires improved scored precision without recall regressions, meaningful
hermetic tests, `make verify`, and the mocked MVP browser pack. Fresh independent
review precedes completion. Live paid dogfood needs an explicit user action.

## Hosted demo

Follow [the hosted demo plan](HOSTED_DEMO_PLAN.md). The existing GitHub Pages hiring
site is a static showcase, separate from the application. A public interactive app
is not considered deployed or ready by a passing local test suite.

## Later, demand-led

- Improve generator output quality and measurement confidence before adding modalities.
- Resume Mood layout/image quality work only after the precision cycle and separate
  cost/acceptance criteria. No automatic generation on upload, login, or navigation.
- Keep geometry on demand; live warm MPS/CUDA acceptance remains separate from mocked
  profile tests. See [geometry gates](P4_GEOMETRY_GATES.md).
- Sessions, collaborative libraries, batch, multimodal inputs, Flutter/Figma product
  surfaces, and additional generative features require their own approved scope.

Historical P0–P5 phase numbering describes prior work rather than the current queue.
Dated implementation reports are in [CHANGELOG.md](../../CHANGELOG.md);
[the review handoff](REVIEW_2026-10-08.md) tracks remaining maintenance and external actions.
