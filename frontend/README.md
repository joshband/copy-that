# Frontend (canonical Vite app)

This directory is the **only** Vite / React package for Copy That.

| Concern | Location |
|--------|----------|
| App entry | `src/main.tsx`, `src/App.tsx` |
| Vite config | `vite.config.ts` |
| TypeScript | `tsconfig.json` (`pnpm type-check` from repo root delegates here) |
| Unit / component tests | Vitest via this package |
| Playwright E2E | `tests/playwright/` + `playwright.config.ts` (invoke from repo root: `pnpm test:e2e`) |

## Commands (from repo root)

```bash
pnpm dev          # → pnpm --dir frontend dev
pnpm build
pnpm type-check
pnpm test
pnpm test:e2e
```

Or from this directory: `pnpm dev`, `pnpm type-check`, etc.

## Deprecated sibling

Repo-root `vite.config.ts` is a fail-fast stub only. Do not add app tooling at the monorepo root.
