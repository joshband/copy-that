# Agent Workflow

How to run coding agents on Copy That. The **rules** are in [`AGENTS.md`](../../AGENTS.md);
this page covers **process**: how a task moves from idea to merged PR, and which agent fits which task.

## One task, one branch, one session

1. **Branch per task.** `git switch -c <type>/<short-name>` off an up-to-date `main`. Use a
   `git worktree` only when two tasks really run in parallel; otherwise one checkout is simpler.
2. **Fresh session per task.** Start each task with a cleared context. Point the agent at
   `AGENTS.md` and the one source-of-truth doc for the area. Don't let it bulk-read `docs/`.
3. **Spec → plan → implement.** For anything multi-file, write a short plan (files to touch, tests to
   add, how you'll verify) before editing. Approve the plan, then implement in small verified steps.
4. **Verify.** Run `make check` after each meaningful edit and `make verify` before calling the work done.
   Claude Code's Stop hook enforces `make check`.
5. **PR.** One logical change per PR. The human approves every commit, push, and merge. CI must
   be green and `main` is protected.
6. **Hand off in writing.** If a task spans sessions, keep a handoff doc (current state, next steps,
   gotchas) under `docs/planning/` and say "continue from <doc>" in the next session. Don't rely on chat
   history.

## Which agent for which task

| Agent | Good for | Setup in this repo |
|-------|----------|--------------------|
| **Claude Code** | Multi-file changes, refactors, debugging, reviews, docs | `CLAUDE.md` (imports `AGENTS.md`), `.claude/settings.json` hooks, `.mcp.json` |
| **Codex / ChatGPT** | Well-specified, self-contained changes; second-opinion reviews | Reads `AGENTS.md` directly |
| **Cursor** | Interactive edits while you're in the editor | `.cursor/rules/*.mdc`, `.cursor/hooks.json` (format on edit) |
| **Local models via LM Studio** | Narrow, file-listed tasks: one function, one test, one doc section | See below |

Whichever agent you use, the definition of done in `AGENTS.md` still applies.

## Local models (LM Studio)

LM Studio serves an OpenAI-compatible API (default `http://localhost:1234/v1`). Point any
OpenAI-compatible agent at it: **Cline**, **Continue**, or **opencode**. Give each one the base URL, any
non-empty API key, and the loaded model's ID.

Small-context models fail on open-ended work. Set them up to succeed:

- **Give an explicit file list** and the exact change. Example: "In `src/copy_that/extractors/spacing/utils.py`,
  make `x` handle an empty list; add a test in `tests/unit/...`." Don't say "improve spacing."
- **Have them read `AGENTS.md` only**, plus the files named in the task.
- **Read large files by range.** Files over ~800 lines (`interfaces/api/colors.py`, `spacing.py`, `w3c.py`)
  don't fit; quote the relevant function in the prompt instead.
- **Run `make check` after every edit** and paste failures back verbatim.
- **Review the diff yourself.** Local models are more likely to delete code silently or invent APIs.

## Context hygiene

- Docs state intent; code holds values. Point agents at `featureFlags.ts` / `infrastructure/ai_models.py`
  rather than restating values in prompts or docs.
- Don't paste `.env` contents into any agent. The rules forbid reading it.
- Historical material lives in `~/Documents/copy-that-archive/`. Only search it when the task asks.
- When a session's context gets long or muddled, write the handoff doc and start fresh. Don't push through.
