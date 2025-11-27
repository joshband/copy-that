#!/usr/bin/env bash
set -euo pipefail

readonly HOST="${HOST:-localhost}"
readonly PORT="${PORT:-8000}"
readonly PROJECT_ID="${PROJECT_ID:-1}"

readonly ENDPOINT="http://${HOST}:${PORT}/api/v1/colors/export/w3c?project_id=${PROJECT_ID}"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required to fetch the W3C export." >&2
  exit 1
fi

readonly OUTPUT_FILE="${OUTPUT_FILE:-}"

response="$(curl -sfL "$ENDPOINT" || true)"
if [[ -z "$response" ]]; then
  echo "Request failed or returned an empty body." >&2
  exit 1
fi

if [[ -n "$OUTPUT_FILE" ]]; then
  echo "$response" >"$OUTPUT_FILE"
  echo "Saved export to $OUTPUT_FILE"
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  echo "$response" | jq -C '
    .color
    | to_entries
    | .[:5]
    | map({id: .key, hex: .value.hex, project_id: .value.project_id, "$type": .value["$type"]})
  '
else
  echo "$response"
fi
