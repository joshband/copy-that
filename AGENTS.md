# AGENTS.md — Copy That

Shared instructions for every coding agent in this repo: Claude Code, OpenAI Codex / ChatGPT,
Cursor, and open-weight models run through LM Studio (Cline, Continue, opencode, …).
Keep this file short and true. It states rules and pointers — **not** status or flag values.

## Product in one line

Screenshot → design tokens (color, spacing, typography, shadow + derived DTCG types) →
W3C / CSS / React / Tailwind / Guide Pack export. Mood and Lighting are opt-in tabs.

## Map

| Path | What |
|------|------|
| `src/copy_that/interfaces/api/` | FastAPI routers (`app_factory.py` mounts them) |
| `src/copy_that/extractors/` | **Canonical** extraction + CV. New extractor code goes here |
| `src/copy_that/application/` | Legacy home being drained into `extractors/` — don't add new modules |
| `src/copy_that/services/` | Business logic (routers should stay thin) |
| `src/copy_that/core_tokens/`, `generators/`, `guide_pack/` | Token graph, W3C adapter, exporters |
| `src/copy_that/infrastructure/ai_models.py` | **Only** place AI model IDs are defined |
| `frontend/src/` | React + Vite + Zustand. Flags: `config/featureFlags.ts` |
| `frontend/tests/playwright/` | The only Playwright home |
| `tests/unit`, `tests/integration` | The only pytest homes CI runs |
| `alembic/` | Migrations — ship one with every schema change |

Source-of-truth docs (read only the one your task needs):
[roadmap](docs/planning/MVP_EXPANSION_ROADMAP.md) ·
[architecture](docs/architecture/CURRENT_ARCHITECTURE_STATE.md) ·
[W3C/DTCG](docs/domain/W3C_CONFORMANCE.md) ·
[env vars](docs/configuration/ENVIRONMENT_VARIABLES.md) ·
[testing](docs/testing/TESTING_GUIDE.md) · [agent workflow](docs/guides/AGENT_WORKFLOW.md)

## Commands

```bash
make install        # locked deps (uv.lock + pnpm-lock) + git hooks
make check          # mypy + ruff + format + tsc + eslint (~1 min)
make verify         # check + full Vitest + pytest unit/integration = everything CI gates
pnpm dev            # UI :5173 · API: python -m uvicorn src.copy_that.interfaces.api.main:app --reload --port 8000
pnpm test:e2e:mvp   # Playwright MVP pack (mocked)
```

## Definition of done

1. `make verify` passes. Not just `pnpm type-check` — CI also runs ruff, format, mypy, eslint, all tests.
2. New behavior has a test in `tests/unit` (backend) or `frontend/src/**/__tests__` (frontend).
3. Docs that describe the change are updated in the same change (see Docs rules).
4. Report honestly: what you ran, what passed, what you skipped.

## Hard rules

- **Never commit, push, merge, or open PRs without explicit approval** from the user in this session.
- Never push to `main`. Work on a branch; one logical change per PR; CI must be green.
- Never read, print, or edit `.env` / `.env.*` (except `.env.example`). Never hard-code keys.
- Never use `--no-verify` to skip hooks. Fix the failure instead.
- Upload extract must never run geometry, FastSAM, UIED, Marigold, or depth models.
- Paid calls (Anthropic, OpenAI, Fal, Flux) only run on explicit user action; never in tests.
- Model IDs come from `copy_that.infrastructure.ai_models` (env-overridable). Don't inline them.
- Tests must be hermetic: no network, no reliance on a developer's `.env` (the root conftest strips it).

## Code style

- Python 3.12, Ruff (100 cols), mypy-clean, typed public functions, snake_case / PascalCase.
- TypeScript strict, React function components, `use*` hooks, no `any` in new code.
- Match the surrounding code's comment density and idiom. Prefer deleting dead code to commenting it out.

## Docs rules

- Docs state **intent and decisions**; code holds **values**. Link to `featureFlags.ts`, don't copy flag values
  (`frontend/src/config/__tests__/docsFlagDrift.test.ts` fails on contradictions).
- Dated "what we did" notes go in `CHANGELOG.md`, not in the roadmap or architecture docs.
- New core doc → add it to `DOCUMENTATION_INDEX.md`. Superseded doc → archive, don't leave it stale.

## Working well with limited context

- Start from this file + the one SoT doc for your area; don't bulk-read `docs/`.
- Large files (>800 lines: `interfaces/api/colors.py`, `spacing.py`, `w3c.py`, …): read by range, search first.
- For multi-file work: write a short plan first, then implement in small verified steps.
- Local / small-context models: take narrowly scoped tasks with an explicit file list; run `make check` after each edit.
