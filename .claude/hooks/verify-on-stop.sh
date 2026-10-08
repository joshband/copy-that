#!/usr/bin/env bash
# Stop: if code changed vs HEAD, run fast gates on what changed and block the
# stop once (exit 2) with the failures, so Claude fixes them before finishing.
# Full gate is `make verify`; this is the cheap subset.
set -u
root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
input="$(cat)"
# Already blocked once this stop — don't loop.
[ "$(printf '%s' "$input" | jq -r '.stop_hook_active // false')" = "true" ] && exit 0
cd "$root" || exit 0

changed="$( { git diff --name-only HEAD; git ls-files --others --exclude-standard; } 2>/dev/null | sort -u)"
py="$(printf '%s\n' "$changed" | grep -E '\.py$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)"
ts="$(printf '%s\n' "$changed" | grep -E '^frontend/.*\.(ts|tsx)$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)"
[ -z "$py" ] && [ -z "$ts" ] && exit 0

out=""
if [ -n "$py" ]; then
  # shellcheck disable=SC2086
  r="$(.venv/bin/ruff check $py 2>&1)" || out+=$'\n## ruff check\n'"$r"
  # shellcheck disable=SC2086
  r="$(.venv/bin/ruff format --check $py 2>&1)" || out+=$'\n## ruff format\n'"$r"
  if printf '%s\n' "$py" | grep -q '^src/'; then
    r="$(.venv/bin/mypy src/ 2>&1)" || out+=$'\n## mypy\n'"$(printf '%s\n' "$r" | tail -20)"
  fi
fi
if [ -n "$ts" ]; then
  r="$(pnpm -s type-check 2>&1)" || out+=$'\n## tsc\n'"$(printf '%s\n' "$r" | tail -20)"
  rel="$(printf '%s\n' "$ts" | sed 's#^frontend/##')"
  # shellcheck disable=SC2086
  r="$(cd frontend && pnpm exec eslint --quiet $rel 2>&1)" || out+=$'\n## eslint\n'"$(printf '%s\n' "$r" | tail -20)"
fi

[ -z "$out" ] && exit 0
printf 'Quality gates failed on changed files — fix before finishing (full gate: make verify):%s\n' "$out" >&2
exit 2
