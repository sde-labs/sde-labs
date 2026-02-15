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
    raise NotImplementedError


def test_week5_config_missing_database_url_raises(monkeypatch):
    """
    TODO:
    - set APP_ENV and API_TOKEN
    - ensure DATABASE_URL is missing
    - assert Settings.from_env() raises ValueError mentioning database_url
    """
    raise NotImplementedError


def test_week5_validation_error_not_retried(memory_conn):
    """
    TODO:
    - call process_alert_event with invalid alert_type
    - assert ValidationError is raised
    - assert no retry warning appears in logs
    """
    raise NotImplementedError


def test_week5_persistence_failure_retries(monkeypatch, memory_conn):
    """
    TODO:
    - monkeypatch insert_alert to fail twice and then succeed
    - call process_alert_event with max_retries=2
    - assert retry warnings are present
    """
    raise NotImplementedError


def test_week5_final_failure_logs_and_raises(monkeypatch, memory_conn):
    """
    TODO:
    - monkeypatch insert_alert to always fail
    - assert RuntimeError is raised after retries are exhausted
    - assert terminal failure log is present
    """
    raise NotImplementedError
