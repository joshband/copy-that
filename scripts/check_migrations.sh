#!/usr/bin/env bash
# Execute Cloud Run migration job and surface logs for staging/production.
set -euo pipefail

ENVIRONMENT="${1:-staging}"
REGION="${REGION:-us-central1}"
JOB="copy-that-migrations-${ENVIRONMENT}"

echo "==> Checking migration job '${JOB}' in region '${REGION}'"
gcloud run jobs describe "${JOB}" --region "${REGION}" --format='value(name)' >/dev/null

echo "==> Executing job (this will block until completion)..."
gcloud run jobs execute "${JOB}" --region "${REGION}" --wait

echo "==> Fetching last execution name..."
LAST_EXEC=$(gcloud run jobs executions list --job "${JOB}" --region "${REGION}" --limit=1 --format='value(name)')
if [[ -z "${LAST_EXEC}" ]]; then
  echo "No executions found for ${JOB}; aborting log fetch." >&2
  exit 1
fi

echo "==> Logs for execution ${LAST_EXEC}:"
gcloud run jobs executions logs read "${LAST_EXEC}" --region "${REGION}"

echo "==> Done."
