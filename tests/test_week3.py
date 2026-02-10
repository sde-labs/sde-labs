"""
Tests for Week 3 assignment - Environment Variables & Secrets
"""
import os
import sys

import pytest
from pydantic import ValidationError

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import Settings


def _set_env(monkeypatch, **values):
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_valid_settings_loaded(monkeypatch):
    _set_env(
        monkeypatch,
        APP_ENV="dev",
        DATABASE_URL="alerts.db",
        API_TOKEN="secret-token",
    )

    settings = Settings.from_env()
    assert settings.env == "dev"
    assert settings.database_url == "alerts.db"
    assert settings.api_token == "secret-token"


def test_missing_required_env_var_rejected(monkeypatch):
    _set_env(
        monkeypatch,
        APP_ENV="dev",
        API_TOKEN="secret-token",
    )

    with pytest.raises(ValueError) as exc_info:
        Settings.from_env()

    error_str = str(exc_info.value)
    assert "database_url" in error_str.lower()


def test_invalid_env_rejected(monkeypatch):
    _set_env(
        monkeypatch,
        APP_ENV="invalid",
        DATABASE_URL="alerts.db",
        API_TOKEN="secret-token",
    )

    with pytest.raises(ValidationError) as exc_info:
        Settings.from_env()

    error_str = str(exc_info.value)
    assert "env" in error_str.lower()


def test_invalid_database_url_rejected(monkeypatch):
    _set_env(
        monkeypatch,
        APP_ENV="test",
        DATABASE_URL="",
        API_TOKEN="secret-token",
    )

    with pytest.raises(ValidationError) as exc_info:
        Settings.from_env()

    error_str = str(exc_info.value)
    assert "database_url" in error_str.lower()


def test_empty_api_token_rejected(monkeypatch):
    _set_env(
        monkeypatch,
        APP_ENV="prod",
        DATABASE_URL="alerts.db",
        API_TOKEN="",
    )

    with pytest.raises(ValidationError) as exc_info:
        Settings.from_env()

    error_str = str(exc_info.value)
    assert "api_token" in error_str.lower()


def test_runtime_env_required_for_ci_secret_flow():
    required = ("APP_ENV", "DATABASE_URL", "API_TOKEN")
    missing = [name for name in required if not os.getenv(name)]

    assert not missing, (
        "Missing required runtime config: "
        + ", ".join(missing)
        + ". Locally use a .env file. In GitHub Actions set repo secrets "
          "(UI: Settings -> Secrets and variables -> Actions, or CLI: gh secret set -f .env)."
    )

    settings = Settings.from_env()

    assert settings.env in {"dev", "test", "prod"}
    assert settings.database_url.endswith(".db")
    assert settings.api_token.strip() != ""
