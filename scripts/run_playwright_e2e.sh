#!/usr/bin/env bash
set -euo pipefail

readonly LOG_DIR="logs"
mkdir -p "$LOG_DIR"

echo "Restarting stack..."
./scripts/restart_dev_stack.sh

echo "Installing Playwright browsers (if needed)..."
(cd frontend && npx playwright install >/dev/null)

echo "Running Playwright tests..."
cd frontend
npx playwright test --config=playwright.config.ts "$@"

echo "Verifying exports..."
cd ..
PORT=8000 ./scripts/verify_export_tokens.sh

echo "Playwright tests finished."
echo "Stopping frontend dev server..."
pkill -f "pnpm --dir frontend run dev" >/dev/null 2>&1 || true
