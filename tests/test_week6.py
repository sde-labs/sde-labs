"""Tests for Week 6 assignment - Auth (Basic, JWT, OAuth)."""
import base64
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.security import auth


def _basic_header(username: str, password: str) -> str:
    raw = f"{username}:{password}".encode("utf-8")
    encoded = base64.b64encode(raw).decode("ascii")
    return f"Basic {encoded}"


def test_parse_basic_auth_header_returns_username_and_password():
    username, password = auth.parse_basic_auth_header(_basic_header("alice", "wonderland"))

    assert username == "alice"
    assert password == "wonderland"


@pytest.mark.parametrize(
    "provided_password,expected",
    [("secret-pass", True), ("wrong-pass", False)],
)
def test_verify_basic_credentials_accepts_valid_and_rejects_invalid(
    provided_password,
    expected,
):
    header = _basic_header("ops-user", provided_password)

    assert auth.verify_basic_credentials(
        header,
        expected_username="ops-user",
        expected_password="secret-pass",
    ) is expected


def test_create_and_verify_hs256_jwt_round_trip():
    now = datetime(2026, 2, 20, 12, 0, 0, tzinfo=timezone.utc)
    token = auth.create_hs256_jwt(
        subject="user-123",
        secret="top-secret",
        expires_in_seconds=120,
        scopes=["alerts:read", "alerts:write"],
        now=now,
    )

    claims = auth.verify_hs256_jwt(token, secret="top-secret", now=now)

    assert claims["sub"] == "user-123"
    assert claims["iat"] == int(now.timestamp())
    assert claims["exp"] == int((now + timedelta(seconds=120)).timestamp())
    assert claims["scope"] == "alerts:read alerts:write"


def test_verify_hs256_jwt_rejects_expired_token():
    issued_at = datetime(2026, 2, 20, 12, 0, 0, tzinfo=timezone.utc)
    token = auth.create_hs256_jwt(
        subject="user-123",
        secret="top-secret",
        expires_in_seconds=1,
        now=issued_at,
    )

    with pytest.raises(ValueError) as exc_info:
        auth.verify_hs256_jwt(
            token,
            secret="top-secret",
            now=issued_at + timedelta(seconds=2),
        )

    assert "expired" in str(exc_info.value).lower()


def test_extract_bearer_token_and_scope_checks():
    token = auth.extract_bearer_token("Bearer abc.def.ghi")
    claims = {"scope": "alerts:read alerts:write"}

    assert token == "abc.def.ghi"
    assert auth.token_has_required_scopes(claims, {"alerts:read"}) is True
    assert auth.token_has_required_scopes(claims, {"admin:write"}) is False
