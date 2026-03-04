# Week 7: Observability — Metrics, Tracing, and Production Health

## Learning Objectives

By the end of this lesson, you will:
- record structured metrics with dimensional tags
- aggregate component health into a single probe response
- measure execution time with nanosecond precision
- apply threshold-based severity classification to numeric signals
- understand how correlation IDs connect requests across services

---

## Why This Week Matters

Logging (Week 4) tells you *what happened*. Observability tells you *why it happened* and *how the system is performing* — even across services you do not control.

Modern production systems run as many small processes: containers on EC2, Lambda functions, ECS tasks. When a request touches five services, a single log line is not enough to reconstruct what went wrong. You need:

- **Metrics** — numeric signals sampled over time (latency, error rate, CPU usage)
- **Traces** — a thread connecting one request across services via a shared ID

Without these, debugging in production is guesswork.

---

## Three Pillars (Logs ✓, Metrics, Traces)

### 1) Production Runtime — Where Your Code Lives

EC2 instances, Docker containers, and serverless functions share one trait: they are ephemeral or replaceable. Orchestrators — Kubernetes, ECS, Lambda — rely on **health probes** to decide whether to send traffic to an instance.

A health endpoint aggregates the status of individual dependencies (database, cache, external API) into one signal the platform can act on:

- all checks pass → `"healthy"` — accept traffic
- any check fails → `"degraded"` — route traffic elsewhere

### 2) Observability — Metrics and Tracing

**Metrics** are named numeric values captured at a point in time, with optional dimensions called **tags**. Tags let you slice a metric by host, region, or environment without emitting separate metrics for each combination:

```python
record_metric("api.latency", 142.3, unit="ms", tags={"region": "us-east-1"})
```

**Tracing** connects one logical request as it moves through multiple services. A **correlation ID** (also called a trace ID or request ID) is generated at the entry point and forwarded in every downstream call via a request header:

```
X-Correlation-Id: 4f3a1b2c-89de-4f01-a3bc-1234567890ab
```

Each service reads the header if present, or creates one if absent. This makes it possible to reconstruct a full request trace across logs from many services.

### 3) Performance — Measuring What Matters

Python's `time.time()` returns a float in seconds, which can lose precision at millisecond granularity due to floating-point representation. Use `time.time_ns()` instead — it returns nanoseconds as a plain integer, then convert at the boundary:

```python
start = time.time_ns()
do_work()
duration_ms = (time.time_ns() - start) / 1_000_000
```

Thresholds translate a raw metric into an actionable severity that alerting systems can act on:

| Value range              | Severity     |
|--------------------------|--------------|
| below warning            | `"ok"`       |
| warning ≤ value < critical | `"warning"` |
| critical ≤ value         | `"critical"` |

---

## Assignment

Implement Week 7 observability helpers in `src/observability/monitor.py`.

### 1) Metrics

- `record_metric(name, value, unit="count", tags=None, now=None) -> dict`
  - Return a dict with keys: `name`, `value`, `unit`, `tags`, `timestamp`
  - `tags` should be `{}` in the returned dict when not provided (never `None`)
  - `timestamp` is an epoch int; use `now` if provided, else `int(time.time())`

### 2) Health and Performance

- `build_health_response(checks: dict[str, bool]) -> dict`
  - Return `{"status": "healthy", "checks": checks}` when all checks are `True`
  - Return `{"status": "degraded", "checks": checks}` when any check is `False`

- `elapsed_ms(start_ns: int, end_ns: int) -> float`
  - Convert nanosecond timestamps to a millisecond duration

- `check_threshold(value: float, warning: float, critical: float) -> str`
  - Return `"ok"`, `"warning"`, or `"critical"` based on which band `value` falls into
  - Boundary values: `warning` maps to `"warning"`, `critical` maps to `"critical"`

---

## Useful Idioms (Keep These)

1. Tags default to `{}`, never `None` — callers should not need to guard against missing tags.

2. Accept `now` for time-dependent functions — keeps tests deterministic without mocking.

3. Fail open on health checks — return a response dict, never raise.

4. Use `time.time_ns()` for timing, convert to ms at the call boundary.

5. Thresholds are inclusive at the lower bound of each band (`>=`, not `>`).

---

## Testing

```bash
pytest tests/test_week7.py -v
pytest tests/ -v
```

---

## Success Criteria

- ✅ Weeks 1–6 tests still pass
- ✅ `record_metric` returns a dict with all five keys; `tags` defaults to `{}`
- ✅ `build_health_response` returns `"degraded"` when any single check fails
- ✅ `elapsed_ms` accepts nanosecond inputs and returns milliseconds
- ✅ `check_threshold` maps boundary values to the correct severity
