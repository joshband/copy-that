# ROADMAP_08.md
# Performance, Cost & ML Inference Optimization

This roadmap focuses on **scaling Copy That safely and efficiently** as usage increases.
It addresses latency, throughput, cost controls, and operational guardrails for AI- and CV-heavy workloads.

---

## 1. Define Performance Budgets (Highest Priority)

### Context
Without explicit budgets, performance regressions and cost creep are invisible until they hurt users or the bill.

### Claude-friendly Issue
Define and enforce **performance budgets** for core operations.

**Budgets to define**
- Image upload → first token latency
- End-to-end extraction time per token type
- Memory ceiling per extraction job
- Cost per extraction (USD)

**Tasks**
- Add timing instrumentation around extractors
- Emit metrics (Prometheus)
- Define alert thresholds

### Acceptance Criteria
- Budgets documented and versioned
- Metrics visible in Grafana
- CI blocks changes that exceed budgets (where feasible)

---

## 2. CPU vs GPU Execution Strategy

### Context
Some extractors (segmentation, CV-heavy steps) benefit from GPU, others do not.
Blind GPU usage increases cost without guaranteed gains.

### Claude-friendly Issue
Introduce a **capability-aware execution strategy**.

**Tasks**
- Classify extractors as CPU-bound vs GPU-accelerated
- Route GPU-eligible steps conditionally
- Benchmark CPU vs GPU paths

### Acceptance Criteria
- GPU only used where net benefit exists
- CPU fallback always available
- Benchmarks documented

---

## 3. Batch vs Streaming Extraction

### Context
Single-image extraction is latency-optimized; batch workloads are throughput-optimized.
They should not share the same execution path.

### Claude-friendly Issue
Separate **batch extraction** from **interactive extraction**.

**Tasks**
- Introduce batch job API
- Queue batch work via Celery
- Tune concurrency independently

### Acceptance Criteria
- Interactive requests remain low-latency under batch load
- Batch jobs scale horizontally
- Queue depth and throughput observable

---

## 4. Aggressive Result Caching

### Context
Identical or near-identical inputs frequently repeat, especially in design iteration workflows.

### Claude-friendly Issue
Implement **multi-layer caching**.

**Cache layers**
- Input hash → extraction result
- Partial extractor outputs
- Token post-processing results

**Tasks**
- Define stable input hashing
- Add Redis-backed cache
- Implement cache invalidation rules

### Acceptance Criteria
- Repeated extractions are significantly faster
- Cache hit rates visible
- No stale or cross-tenant leakage

---

## 5. Cost Controls & Quotas

### Context
AI inference costs scale with usage; guardrails are mandatory for SaaS viability.

### Claude-friendly Issue
Add **cost visibility and enforcement**.

**Tasks**
- Track per-request cost (Claude, Vision APIs)
- Aggregate cost per project/tenant
- Enforce quotas and rate limits

### Acceptance Criteria
- Cost metrics visible per tenant
- Hard and soft limits enforced
- Overages blocked or throttled

---

## 6. Model Selection & Degradation Paths

### Context
Not all users need the highest-fidelity extraction every time.

### Claude-friendly Issue
Introduce **quality tiers** with graceful degradation.

**Tasks**
- Define extraction quality tiers
- Map tiers to models/algorithms
- Expose tier selection in API/UI

### Acceptance Criteria
- Lower tiers reduce cost and latency
- Higher tiers preserve accuracy
- Behavior documented and testable

---

## 7. Memory & Concurrency Limits

### Context
Unbounded concurrency can OOM containers and cascade failures.

### Claude-friendly Issue
Add **explicit concurrency and memory controls**.

**Tasks**
- Limit concurrent extraction jobs
- Enforce per-job memory ceilings
- Configure Cloud Run concurrency intentionally

### Acceptance Criteria
- No OOM under load tests
- Predictable degradation under stress
- Limits documented

---

## 8. Load Testing & Failure Drills

### Context
Systems fail in production in ways tests don’t cover.

### Claude-friendly Issue
Introduce **load testing and chaos scenarios**.

**Tasks**
- Simulate high extraction load
- Kill workers during active jobs
- Validate retry and idempotency

### Acceptance Criteria
- System recovers from partial failure
- No data corruption
- Failure modes documented

---

## Suggested Execution Order

1. Performance budgets
2. Caching
3. Cost tracking & quotas
4. CPU/GPU routing
5. Batch extraction separation
6. Quality tiers
7. Concurrency limits
8. Load & failure testing

---

## Outcome

After ROADMAP_08:
- Performance is predictable
- Costs are controlled and visible
- Scaling is intentional, not accidental
- Copy That is SaaS-ready under real load
