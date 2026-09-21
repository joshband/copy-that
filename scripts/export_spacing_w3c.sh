#!/usr/bin/env bash
set -euo pipefail

readonly HOST="${HOST:-localhost}"
readonly PORT="${PORT:-8000}"
readonly OUTPUT_FILE="${OUTPUT_FILE:-}"
readonly ENDPOINT="http://${HOST}:${PORT}/api/v1/spacing/export/w3c"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required to fetch the spacing export." >&2
  exit 1
fi

response="$(curl -sfL "$ENDPOINT" || true)"
if [[ -z "$response" ]]; then
  echo "Request failed or returned an empty body." >&2
  exit 1
fi

if [[ -n "$OUTPUT_FILE" ]]; then
  echo "$response" >"$OUTPUT_FILE"
  echo "Saved spacing export to $OUTPUT_FILE"
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  echo "$response" | jq -C '
    .spacing
    | to_entries
    | .[:5]
    | map({id: .key, value: .value.value, project_id: .value.project_id})
  '
else
  echo "$response"
fi
