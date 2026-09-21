/**
 * DEPRECATED (2026-09-19) — dual Vite roots collapsed.
 *
 * Canonical Vite app + config: `frontend/` (`frontend/vite.config.ts`).
 * Root scripts (`pnpm dev`, `pnpm build`, `pnpm type-check`) delegate with
 * `pnpm --dir frontend …`. Do not add app config here.
 *
 * This file exists only to fail fast if someone runs `vite` from the repo root.
 */
throw new Error(
  'Vite app lives in frontend/. Use `pnpm dev` (or `pnpm --dir frontend dev`). Canonical config: frontend/vite.config.ts',
)
