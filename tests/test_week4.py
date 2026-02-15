"""
Tests for Week 4 assignment - Error Handling and Logging
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
from src.infrastructure.repositories import get_all_alerts


def test_settings_default_log_level_is_info():
    settings = Settings(
        env="dev",
        database_url="alerts.db",
        api_token="secret-token",
    )

    assert settings.log_level == "INFO"


def test_settings_invalid_log_level_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            env="dev",
            database_url="alerts.db",
            api_token="secret-token",
            log_level="VERBOSE",
        )

    assert "log_level" in str(exc_info.value).lower()


def test_from_env_defaults_log_level_to_info(monkeypatch):
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("DATABASE_URL", "alerts.db")
    monkeypatch.setenv("API_TOKEN", "secret-token")
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    settings = Settings.from_env()
    assert settings.log_level == "INFO"


def test_load_settings_delegates_to_settings_from_env(monkeypatch):
    sentinel = object()

    def fake_from_env(cls):
        return sentinel

    monkeypatch.setattr(Settings, "from_env", classmethod(fake_from_env))

    assert app.load_settings() is sentinel


def test_process_alert_reading_wires_domain_and_infra():
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)

    app.process_alert_reading(
        conn,
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_001",
        alert_type="LEAK",
        latitude=29.7604,
        longitude=-95.3698,
    )

    alerts = get_all_alerts(conn)
    assert len(alerts) == 1
    assert alerts[0][2] == "LEAK"
    assert alerts[0][3] == "CRITICAL"


def test_build_logger_uses_timestamp_level_message_format():
    stream = io.StringIO()

    logger = app.build_logger("INFO", stream=stream)
    logger.info("hello")

    output = stream.getvalue().strip()
    parts = output.split(",", 2)

    assert len(parts) == 3
    assert parts[1] == "INFO"
    assert parts[2] == "hello"


def test_build_logger_debug_visible_when_level_is_debug():
    stream = io.StringIO()

    logger = app.build_logger("DEBUG", stream=stream)
    logger.debug("debug_line")

    assert "DEBUG,debug_line" in stream.getvalue()


def test_build_logger_debug_hidden_when_level_is_info():
    stream = io.StringIO()

    logger = app.build_logger("INFO", stream=stream)
    logger.debug("debug_line")

    assert "debug_line" not in stream.getvalue()


def test_process_alert_event_happy_path_logs_and_persists():
    stream = io.StringIO()
    logger = app.build_logger("DEBUG", stream=stream)
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)

    alert = app.process_alert_event(
        conn,
        logger,
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_001",
        alert_type="LEAK",
        latitude=29.7604,
        longitude=-95.3698,
    )

    alerts = get_all_alerts(conn)
    output = stream.getvalue()

    assert alert.severity == "CRITICAL"
    assert len(alerts) == 1
    assert "processing_alert" in output
    assert "alert_recorded" in output


def test_process_alert_event_logs_validation_failure_with_exception():
    stream = io.StringIO()
    logger = app.build_logger("DEBUG", stream=stream)
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)

    with pytest.raises(ValidationError):
        app.process_alert_event(
            conn,
            logger,
            timestamp="2024-01-26T10:00:00Z",
            site_id="SITE_002",
            alert_type="NOT_A_REAL_TYPE",
            latitude=29.7604,
            longitude=-95.3698,
        )

    output = stream.getvalue()
    assert "validation_failed" in output
    assert "Traceback" in output


def test_process_alert_event_retries_then_succeeds(monkeypatch):
    stream = io.StringIO()
    logger = app.build_logger("DEBUG", stream=stream)
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)

    attempts = {"count": 0}

    def flaky_insert_alert(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("temporary db failure")

    monkeypatch.setattr(app, "insert_alert", flaky_insert_alert)

    alert = app.process_alert_event(
        conn,
        logger,
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_003",
        alert_type="LEAK",
        latitude=29.7604,
        longitude=-95.3698,
        max_retries=2,
    )

    output = stream.getvalue()
    assert alert.severity == "CRITICAL"
    assert attempts["count"] == 2
    assert "retrying_persist" in output
    assert "alert_recorded" in output


def test_process_alert_event_logs_runtime_failure_after_retries(monkeypatch):
    stream = io.StringIO()
    logger = app.build_logger("DEBUG", stream=stream)
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)

    attempts = {"count": 0}

    def fake_insert_alert(*args, **kwargs):
        attempts["count"] += 1
        raise RuntimeError("database write failed")

    monkeypatch.setattr(app, "insert_alert", fake_insert_alert)

    with pytest.raises(RuntimeError):
        app.process_alert_event(
            conn,
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
    assert "alert_processing_failed" in output
    assert "Traceback" in output
