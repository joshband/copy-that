#!/usr/bin/env bash
# PostToolUse (Edit|Write|MultiEdit): format the file Claude just changed.
# Python → ruff fix + format (project .venv); TS/TSX → eslint --fix (frontend).
# Never blocks: formatting problems surface later in `make check`.
set -u
root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
# Claude Code sends tool_input.file_path; Cursor's afterFileEdit sends file_path.
file="$(jq -r '.tool_response.filePath // .tool_input.file_path // .file_path // empty')"
[ -n "$file" ] && [ -f "$file" ] || exit 0
case "$file" in "$root"/*) ;; *) exit 0 ;; esac

case "$file" in
  *.py)
    "$root/.venv/bin/ruff" check --fix --quiet "$file" >/dev/null 2>&1
    "$root/.venv/bin/ruff" format --quiet "$file" >/dev/null 2>&1
    ;;
  "$root"/frontend/*.ts|"$root"/frontend/*.tsx)
    (cd "$root/frontend" && pnpm exec eslint --fix --quiet "$file" >/dev/null 2>&1)
    ;;
esac
exit 0
