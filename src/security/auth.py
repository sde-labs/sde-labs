"""Authentication helpers for Week 6.

Week 6 focus:
- Basic auth parsing and credential verification
- JWT creation/verification with HS256
- OAuth-style bearer token and scope checks
"""
import base64
import binascii
import hashlib
import hmac
import json
from datetime import datetime
from datetime import timezone


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded)


def parse_basic_auth_header(auth_header: str) -> tuple[str, str]:
    """Parse a Basic auth header into username/password.

    Expected format:
    - Authorization header value: "Basic <base64(username:password)>"

    Raise ValueError when the header is missing/malformed.
    """
    try:
        scheme, _, encoded = auth_header.partition(" ")
        if scheme.lower() != "basic" or not encoded:
            raise ValueError("Malformed Basic auth header")
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, _, password = decoded.partition(":")
        if not username:
            raise ValueError("Malformed Basic auth header")
        return username, password
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise ValueError("Malformed Basic auth header") from exc


def verify_basic_credentials(
    auth_header: str,
    expected_username: str,
    expected_password: str,
) -> bool:
    """Verify Basic auth credentials against expected values.

    Requirements:
    - Parse credentials using parse_basic_auth_header
    - Use constant-time string comparisons
    - Return True on match, else False
    """
    try:
        username, password = parse_basic_auth_header(auth_header)
    except ValueError:
        return False
    username_ok = hmac.compare_digest(username, expected_username)
    password_ok = hmac.compare_digest(password, expected_password)
    return username_ok and password_ok


def create_hs256_jwt(
    subject: str,
    secret: str,
    expires_in_seconds: int = 3600,
    scopes: list[str] | None = None,
    now: datetime | None = None,
) -> str:
    """Create a signed JWT string using HS256.

    Minimum claims:
    - sub: subject
    - iat: issued-at epoch seconds
    - exp: expiration epoch seconds
    - scope: space-separated scopes (optional)

    Notes:
    - Use URL-safe base64 without padding for JWT segments.
    - The JWT header should include {"alg": "HS256", "typ": "JWT"}.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    iat = int(now.timestamp())
    exp = iat + expires_in_seconds

    header = {"alg": "HS256", "typ": "JWT"}
    payload: dict = {"sub": subject, "iat": iat, "exp": exp}
    if scopes:
        payload["scope"] = " ".join(scopes)

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()

    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_hs256_jwt(token: str, secret: str, now: datetime | None = None) -> dict:
    """Verify an HS256 JWT and return claims.

    Validation requirements:
    - token has 3 segments
    - signature is valid
    - exp exists and has not expired

    Raise ValueError for invalid tokens.
    """
    segments = token.split(".")
    if len(segments) != 3:
        raise ValueError("Invalid JWT: must have 3 segments")

    header_b64, payload_b64, sig_b64 = segments
    signing_input = f"{header_b64}.{payload_b64}".encode()

    expected_sig = hmac.new(
        secret.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    try:
        actual_sig = _b64url_decode(sig_b64)
    except Exception as exc:
        raise ValueError("Invalid JWT signature encoding") from exc

    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("Invalid JWT signature")

    try:
        claims = json.loads(_b64url_decode(payload_b64))
    except Exception as exc:
        raise ValueError("Invalid JWT payload") from exc

    if "exp" not in claims:
        raise ValueError("Invalid JWT: missing exp claim")

    if now is None:
        now = datetime.now(timezone.utc)
    if int(now.timestamp()) >= claims["exp"]:
        raise ValueError("JWT expired")

    return claims


def extract_bearer_token(auth_header: str) -> str:
    """Extract a bearer token from an Authorization header.

    Expected format:
    - "Bearer <token>"

    Raise ValueError when header is missing/malformed.
    """
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise ValueError("Malformed Bearer auth header")
    return token


def token_has_required_scopes(claims: dict, required_scopes: set[str]) -> bool:
    """Check whether token claims satisfy required OAuth scopes.

    Support either claim style:
    - scope: "space separated scopes"
    - scopes: ["scope:a", "scope:b"]

    Return True only when all required scopes are present.
    """
    if "scope" in claims:
        granted = set(claims["scope"].split())
    elif "scopes" in claims:
        granted = set(claims["scopes"])
    else:
        granted = set()
    return required_scopes.issubset(granted)
