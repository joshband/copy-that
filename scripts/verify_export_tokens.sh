#!/usr/bin/env bash
set -euo pipefail

readonly PORT="${PORT:-8000}"
COLOR_OUT="$(mktemp)"
SPACING_OUT="$(mktemp)"

cleanup() {
  rm -f "$COLOR_OUT" "$SPACING_OUT"
}

trap cleanup EXIT

echo "Verifying color export..."
./scripts/export_colors_w3c.sh PORT="$PORT" OUTPUT_FILE="$COLOR_OUT"
color_count=$(jq '.color | length' "$COLOR_OUT")
if [[ "$color_count" -eq 0 ]]; then
  echo "Color export empty" >&2
  exit 1
fi

echo "Verifying spacing export..."
./scripts/export_spacing_w3c.sh PORT="$PORT" OUTPUT_FILE="$SPACING_OUT"
spacing_count=$(jq '.spacing | length' "$SPACING_OUT")
if [[ "$spacing_count" -eq 0 ]]; then
  echo "Spacing export empty" >&2
  exit 1
fi

echo "Exports verified: $color_count colors, $spacing_count spacing tokens"
