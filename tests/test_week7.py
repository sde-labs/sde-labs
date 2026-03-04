"""Tests for Week 7 assignment - Observability."""
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.observability import monitor


def test_record_metric_returns_expected_shape():
    m = monitor.record_metric(
        "cpu.usage",
        72.5,
        unit="percent",
        tags={"host": "web-01"},
        now=1_700_000_000,
    )
    assert m["name"] == "cpu.usage"
    assert m["value"] == 72.5
    assert m["unit"] == "percent"
    assert m["tags"] == {"host": "web-01"}
    assert m["timestamp"] == 1_700_000_000


@pytest.mark.parametrize(
    "checks,expected_status",
    [
        ({"db": True, "cache": True}, "healthy"),
        ({"db": True, "cache": False}, "degraded"),
        ({"db": False, "cache": False}, "degraded"),
    ],
)
def test_build_health_response_aggregates_status(checks, expected_status):
    response = monitor.build_health_response(checks)
    assert response["status"] == expected_status
    assert response["checks"] == checks


def test_elapsed_ms_returns_duration_in_milliseconds():
    start = 1_000_000_000
    end = 1_250_000_000
    assert monitor.elapsed_ms(start, end) == pytest.approx(250.0)


@pytest.mark.parametrize(
    "value,warning,critical,expected",
    [
        (10.0, 70.0, 90.0, "ok"),
        (75.0, 70.0, 90.0, "warning"),
        (95.0, 70.0, 90.0, "critical"),
        (70.0, 70.0, 90.0, "warning"),
        (90.0, 70.0, 90.0, "critical"),
    ],
)
def test_check_threshold_returns_correct_severity(value, warning, critical, expected):
    assert monitor.check_threshold(value, warning, critical) == expected
