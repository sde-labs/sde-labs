"""Observability helpers for Week 7.

Week 7 focus:
- Structured metrics with dimensional tags
- Distributed tracing via correlation IDs
- Health check aggregation
- High-resolution performance timing
- Threshold-based severity classification
"""
import time
import uuid


def record_metric(
    name: str,
    value: float,
    unit: str = "count",
    tags: dict | None = None,
    now: int | None = None,
) -> dict:
    """Record a named metric with optional dimensions.

    Requirements:
    - Return a dict with keys: name, value, unit, tags, timestamp
    - tags should default to {} (not None) in the returned dict
    - timestamp is an epoch int; use now if provided, else time.time()
    """
    return {
        "name": name,
        "value": value,
        "unit": unit,
        "tags": tags if tags is not None else {},
        "timestamp": now if now is not None else int(time.time()),
    }


def build_health_response(checks: dict[str, bool]) -> dict:
    """Aggregate component checks into a health response.

    Requirements:
    - Return {"status": "healthy", "checks": checks} when all are True
    - Return {"status": "degraded", "checks": checks} when any are False
    """
    status = "healthy" if all(checks.values()) else "degraded"
    return {"status": status, "checks": checks}


def elapsed_ms(start_ns: int, end_ns: int) -> float:
    """Compute elapsed time in milliseconds from nanosecond timestamps.

    Use time.time_ns() to capture start/end values.
    Convert: (end_ns - start_ns) / 1_000_000
    """
    return (end_ns - start_ns) / 1_000_000


def check_threshold(value: float, warning: float, critical: float) -> str:
    """Classify a metric value against warning and critical thresholds.

    Return:
    - "ok"       when value < warning
    - "warning"  when warning <= value < critical
    - "critical" when value >= critical
    """
    if value >= critical:
        return "critical"
    if value >= warning:
        return "warning"
    return "ok"
