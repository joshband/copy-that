# Copy That - Roadmap (Current)

**Status:** v0.4.0 released | Color token pipeline production-ready | Sessions/libraries/exports live
**Last Updated:** 2025-11-21

## Milestones

### Now (v0.4.x)
- Stabilize session/library/export flows (w3c/css/react/html)
- Frontend polish: educational components, inspector/playground refinements
- Ops: finalize runbook, troubleshooting, Terraform/Alembic docs

### Next (Phase 5)
- Spacing tokens (schema, extractor, export) with SAM-assisted detection
- Typography tokens (schema, extractor, export)
- API examples & quickstart scripts for new token types

### Later (Phase 6+)
- Component tokens (button/input/card detection)
- Multi-modal inputs (video/audio/text) feeding token pipelines
- Plugins (Figma/Sketch) and CI-based export validation

## Testing & Quality
- Maintain backend/unit/integration/e2e coverage; keep `tests/scripts/` for targeted runs
- Performance: tune batch extraction, index DB paths, cache where safe

## Ops & Deployment
- Use runbook (`docs/ops/runbook.md`) and Terraform (`terraform/README.md`)
- Keep `.env.example` current; rotate secrets regularly

## Documentation
- Entry points: `docs/overview/documentation.md`, `docs/overview/library_index.md`
- API examples: `docs/examples/api_curl.md`
- Design: `docs/design/minimalist_design_guide.md` + `design/legacy` for history
