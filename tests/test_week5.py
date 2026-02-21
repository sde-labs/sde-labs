"""
Tests for Week 5 assignment - Writing robust tests
"""
import io
import os
import sqlite3
import sys

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.main as app
from src.config.settings import Settings
from src.infrastructure.database import initialize_database


@pytest.fixture
def memory_conn():
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)
    yield conn
    conn.close()


@pytest.mark.parametrize(
    "log_level,expected_debug",
    [("DEBUG", True), ("INFO", False)],
)
def test_week5_log_level_behavior(log_level, expected_debug):
    """
    TODO:
    - build a logger with the provided log_level
    - emit a debug message
    - assert whether it appears based on expected_debug
    """
    stream = io.StringIO()
    logger = app.build_logger(log_level, stream=stream)
    logger.debug("debug_line")

    assert ("debug_line" in stream.getvalue()) is expected_debug


def test_week5_config_missing_database_url_raises(monkeypatch):
    """
    TODO:
    - set APP_ENV and API_TOKEN
    - ensure DATABASE_URL is missing
    - assert Settings.from_env() raises ValueError mentioning database_url
    """
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("API_TOKEN", "secret-token")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValueError) as exc_info:
        Settings.from_env()

    assert "database_url" in str(exc_info.value).lower()


def test_week5_validation_error_not_retried(memory_conn):
    """
    TODO:
    - call process_alert_event with invalid alert_type
    - assert ValidationError is raised
    - assert no retry warning appears in logs
    """
    stream = io.StringIO()
    logger = app.build_logger("DEBUG", stream=stream)

    with pytest.raises(ValidationError):
        app.process_alert_event(
            memory_conn,
            logger,
            timestamp="2024-01-26T10:00:00Z",
            site_id="SITE_002",
            alert_type="NOT_A_REAL_TYPE",
            latitude=29.7604,
            longitude=-95.3698,
            max_retries=2,
        )

    output = stream.getvalue()
    assert "validation_failed" in output
    assert "retrying_persist" not in output


def test_week5_persistence_failure_retries(monkeypatch, memory_conn):
    """
    TODO:
    - monkeypatch insert_alert to fail twice and then succeed
    - call process_alert_event with max_retries=2
    - assert retry warnings are present
    """
    stream = io.StringIO()
    logger = app.build_logger("DEBUG", stream=stream)
    attempts = {"count": 0}

    def flaky_insert_alert(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] <= 2:
            raise RuntimeError("temporary db failure")

    monkeypatch.setattr(app, "insert_alert", flaky_insert_alert)

    app.process_alert_event(
        memory_conn,
        logger,
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_003",
        alert_type="LEAK",
        latitude=29.7604,
        longitude=-95.3698,
        max_retries=2,
    )

    output = stream.getvalue()
    assert attempts["count"] == 3
    assert output.count("retrying_persist") == 2
    assert "alert_recorded" in output


def test_week5_final_failure_logs_and_raises(monkeypatch, memory_conn):
    """
    TODO:
    - monkeypatch insert_alert to always fail
    - assert RuntimeError is raised after retries are exhausted
    - assert terminal failure log is present
    """
    stream = io.StringIO()
    logger = app.build_logger("DEBUG", stream=stream)
    attempts = {"count": 0}

    def always_fail_insert_alert(*args, **kwargs):
        attempts["count"] += 1
        raise RuntimeError("database write failed")

    monkeypatch.setattr(app, "insert_alert", always_fail_insert_alert)

    with pytest.raises(RuntimeError):
        app.process_alert_event(
            memory_conn,
            logger,
            timestamp="2024-01-26T10:00:00Z",
            site_id="SITE_004",
            alert_type="LEAK",
            latitude=29.7604,
            longitude=-95.3698,
            max_retries=2,
        )

    output = stream.getvalue()
    assert attempts["count"] == 3
    assert output.count("retrying_persist") == 2
    assert "alert_processing_failed" in output
