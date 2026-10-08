# Copy That — Claude Code

**Version:** 2.0.0
**Last Updated:** 2026-10-08

All shared agent rules live in AGENTS.md (also read by Codex, Cursor, and local-model agents):

@AGENTS.md

## Claude Code specifics

- **Before ending a task:** `make verify` must pass. The Stop hook runs `make check` and blocks the stop if it fails.
- **Never** auto-commit / push without explicit approval.
- Edited files are auto-formatted by the PostToolUse hook (`.claude/hooks/format-edited-file.sh`); don't hand-format.
- Project MCP servers: `.mcp.json`. Shared permissions + hooks: `.claude/settings.json`; personal overrides go in `.claude/settings.local.json` (gitignored).
- Multi-file change → plan mode or a written plan first. Subagents / worktrees only for genuinely parallel work.
- Mood board local image default: `dhairyashil/FLUX.1-schnell-mflux-4bit` (Z-Image opt-in only).
- Historical docs live in `~/Documents/copy-that-archive/` — don't search it unless asked.
