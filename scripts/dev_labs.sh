#!/usr/bin/env bash
# Start the Labs / mood-board local stack against the CANONICAL Vite frontend.
#
# Canonical UI:  http://127.0.0.1:5173   (pnpm --dir frontend / root `pnpm dev`)
# Docker UI:     http://127.0.0.1:3000   (compose `frontend` image — often stale; not default)
# API:           http://127.0.0.1:8000
# Fal Flux shim: http://127.0.0.1:8766
#
# Usage:
#   ./scripts/dev_labs.sh              # infra + fal shim + API + Vite (foreground Vite)
#   ./scripts/dev_labs.sh --check      # print status only
#   ./scripts/dev_labs.sh --no-vite    # everything except frontend
#   ./scripts/dev_labs.sh --with-celery  # also start mood-board Celery solo worker
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CHECK_ONLY=0
NO_VITE=0
WITH_CELERY=0
for arg in "$@"; do
  case "$arg" in
    --check) CHECK_ONLY=1 ;;
    --no-vite) NO_VITE=1 ;;
    --with-celery) WITH_CELERY=1 ;;
    -h|--help)
      sed -n '2,20p' "$0"
      exit 0
      ;;
  esac
done

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

have_port() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

echo "=== Copy That Labs stack ==="
echo "Canonical frontend: http://127.0.0.1:5173  (Vite / frontend/)"
echo "Docker frontend:    http://127.0.0.1:3000  (compose image — use only if intentional)"
echo

status_line() {
  local name="$1" port="$2"
  if have_port "$port"; then
    echo "  OK   $name :$port"
  else
    echo "  --   $name :$port"
  fi
}

status_line "postgres (host)" 5432
status_line "redis" 6379
status_line "API" 8000
status_line "Fal shim" 8766
status_line "Vite UI" 5173
status_line "Docker UI" 3000

if [[ -z "${FAL_KEY:-}" ]]; then
  echo
  echo "WARN: FAL_KEY unset — Flux cloud path disabled. Set in .env (https://fal.ai/dashboard/keys)"
else
  echo
  echo "  OK   FAL_KEY is set"
fi

if [[ -z "${MOOD_BOARD_FLUX_BASE_URL:-}" ]]; then
  echo "WARN: MOOD_BOARD_FLUX_BASE_URL unset — recommend http://127.0.0.1:8766/v1"
else
  echo "  OK   MOOD_BOARD_FLUX_BASE_URL=${MOOD_BOARD_FLUX_BASE_URL}"
fi

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  exit 0
fi

# --- infra ---
if command -v docker >/dev/null 2>&1; then
  if ! have_port 5432 || ! have_port 6379; then
    echo
    echo "→ docker compose up -d postgres redis"
    docker compose up -d postgres redis
    sleep 2
  fi
fi

# --- Fal shim ---
if [[ -n "${FAL_KEY:-}" ]]; then
  export MOOD_BOARD_FLUX_BASE_URL="${MOOD_BOARD_FLUX_BASE_URL:-http://127.0.0.1:8766/v1}"
  export MOOD_BOARD_FLUX_API_KEY="${MOOD_BOARD_FLUX_API_KEY:-local}"
  export MOOD_BOARD_FLUX_MODEL="${MOOD_BOARD_FLUX_MODEL:-flux-schnell}"
  if ! have_port 8766; then
    echo "→ Fal shim :8766"
    .venv/bin/python scripts/mood_board_fal_openai_shim.py >/tmp/copy_that_fal_shim.log 2>&1 &
    sleep 1
  fi
fi

# --- API ---
if ! have_port 8000; then
  echo "→ API :8000"
  PYTHONPATH=src .venv/bin/uvicorn copy_that.interfaces.api.main:app \
    --host 127.0.0.1 --port 8000 >/tmp/copy_that_api.log 2>&1 &
  sleep 2
fi

# --- Celery (optional) ---
if [[ "$WITH_CELERY" -eq 1 ]]; then
  if pgrep -f 'celery.*mood-board' >/dev/null 2>&1; then
    echo "  OK   celery mood-board already running"
  else
    echo "→ Celery mood-board (solo)"
    PYTHONPATH=src .venv/bin/celery -A copy_that.infrastructure.celery.app worker \
      --loglevel=info -Q mood-board,celery --pool=solo >/tmp/copy_that_celery_mood.log 2>&1 &
    sleep 2
  fi
fi

# --- health probe ---
if have_port 8000; then
  echo
  echo "→ mood-board health backends:"
  curl -fsS "http://127.0.0.1:8000/api/v1/mood-board/health" \
    | .venv/bin/python -c "import sys,json; d=json.load(sys.stdin); print([(b['id'], b['available']) for b in d.get('backends',[])])" \
    || echo "  (health check failed — see /tmp/copy_that_api.log)"
fi

if [[ "$NO_VITE" -eq 1 ]]; then
  echo
  echo "Done (--no-vite). Open UI with: pnpm dev   → http://127.0.0.1:5173"
  exit 0
fi

if have_port 5173; then
  echo
  echo "Vite already on :5173 — open http://127.0.0.1:5173 (Overview → Labs)"
  exit 0
fi

echo
echo "→ Vite frontend (canonical) http://127.0.0.1:5173"
echo "   Do NOT use :3000 unless you intentionally rebuilt the Docker frontend image."
exec pnpm --dir frontend dev
