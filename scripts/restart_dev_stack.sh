#!/usr/bin/env bash
set -euo pipefail

readonly LOG_DIR="logs"
readonly VITE_LOG="${LOG_DIR}/vite.log"

mkdir -p "$LOG_DIR"

echo "Stopping local backend/frontend processes..."
pkill -f "uvicorn src.copy_that.interfaces.api.main:app" >/dev/null 2>&1 || true
pkill -f "pnpm --dir frontend run dev" >/dev/null 2>&1 || true

echo "Restarting API (docker compose up -d api)..."
docker compose stop api >/dev/null 2>&1 || true
docker compose up -d api >/dev/null

echo "Launching frontend (pnpm run dev)..."
if pgrep -f "pnpm --dir frontend run dev" >/dev/null 2>&1; then
  echo "Frontend already running; restarting..."
  pkill -f "pnpm --dir frontend run dev" >/dev/null 2>&1 || true
fi

pnpm --dir frontend run dev -- --host 0.0.0.0 --port 5173 >"$VITE_LOG" 2>&1 &
FRONTEND_PID=$!
sleep 2

echo "Frontend URL: http://localhost:5173"
echo "API export helper: ./scripts/export_colors_w3c.sh (pass PORT=<docker-port> if needed)"
echo "Vite log: $VITE_LOG (tail -f $VITE_LOG to watch console output)"
echo "Frontend PID: $FRONTEND_PID"
