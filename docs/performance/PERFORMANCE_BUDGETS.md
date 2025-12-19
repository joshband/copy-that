# PERFORMANCE_BUDGETS.md
# Copy That – Performance Budgets & Instrumentation (Dec 2025)

These budgets set expectations for latency, memory, and cost. They are enforced via
runtime logging and can be promoted to hard failures in CI by setting
`PERF_BUDGET_ENFORCE=true`.

---

## Budgets (initial targets)
- Image upload → first token: **< 2s** (p50)
- End-to-end color extraction per request: **< 10s** (p95)
- Spacing/shadow extraction per request: **< 10s** (p95)
- Memory per extraction job: **< 512MB**
- Cost per extraction (LLM+CV): **< $0.05**

---

## Instrumentation
- `src/copy_that/application/perf.py` provides `track_perf()` context manager with budgets:
  - `extract.color.ai` (10s)
  - `extract.spacing.ai` (10s)
  - `extract.shadow.ai` (10s)
  - `upload.first_token` (2s placeholder; wire where applicable)
- Extractors emit structured log payloads under the `perf` key:
  - `metric`: `perf_ms`
  - `operation`: budget key
  - `duration_ms`
  - `budget_ms` / `over_budget` (when defined)
  - `attrs`: model, max tokens, etc.
- When `PERF_BUDGET_ENFORCE=true`, exceeding a budget raises `RuntimeError`
  (intended for CI/regression checks).

---

## How to use in CI
- Export `PERF_BUDGET_ENFORCE=true` for targeted perf smoke tests:
  ```bash
  PERF_BUDGET_ENFORCE=true pytest tests/performance  # or targeted extractor calls
  ```
- Parse logs for `perf_timing` entries to trend durations and catch regressions.
- Consider adding a small perf smoke (fixed image) to CI to assert budgets.

---

## Alerting & Thresholds
- Alert when `over_budget=true` for any operation for 5+ occurrences per 15 minutes.
- Watch memory at the workload level (512MB ceiling) via Cloud Run / Prometheus.
- Track cost per extraction by sampling LLM usage (token counts) and mapping to <$0.05.

---

## Next Steps
- Wire `upload.first_token` around the upload→extract pipeline.
- Add Prometheus counters/histograms for `perf_ms` per operation.
- Add fixed-input perf smoke tests to CI to gate regressions.
- Tune budgets with real telemetry before tightening.
