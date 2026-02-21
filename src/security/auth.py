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
    if not auth_header or not auth_header.strip():
        raise ValueError("Missing Authorization header")

    parts = auth_header.strip().split(None, 1)
    if len(parts) != 2:
        raise ValueError("Malformed Authorization header")

    scheme, encoded = parts
    if scheme.lower() != "basic":
        raise ValueError("Authorization scheme must be Basic")

    try:
        decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise ValueError("Malformed Basic credentials") from exc

    username, separator, password = decoded.partition(":")
    if separator != ":" or not username:
        raise ValueError("Malformed Basic credentials")

    return username, password


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

    return hmac.compare_digest(username, expected_username) and hmac.compare_digest(
        password,
        expected_password,
    )


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
    issued_at = now or datetime.now(timezone.utc)
    iat = int(issued_at.timestamp())
    exp = iat + expires_in_seconds

    header = {"alg": "HS256", "typ": "JWT"}
    claims = {
        "sub": subject,
        "iat": iat,
        "exp": exp,
    }
    if scopes:
        claims["scope"] = " ".join(scopes)

    header_b64 = _b64url_encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    payload_b64 = _b64url_encode(
        json.dumps(claims, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def verify_hs256_jwt(token: str, secret: str, now: datetime | None = None) -> dict:
    """Verify an HS256 JWT and return claims.

    Validation requirements:
    - token has 3 segments
    - signature is valid
    - exp exists and has not expired

    Raise ValueError for invalid tokens.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT structure")

    header_b64, payload_b64, signature_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")

    try:
        header = json.loads(_b64url_decode(header_b64).decode("utf-8"))
        claims = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        signature = _b64url_decode(signature_b64)
    except (binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("Malformed JWT") from exc

    if header.get("alg") != "HS256":
        raise ValueError("Unsupported JWT algorithm")

    expected_signature = hmac.new(
        secret.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("Invalid JWT signature")

    if "exp" not in claims:
        raise ValueError("JWT missing exp claim")

    current_time = int((now or datetime.now(timezone.utc)).timestamp())
    if current_time >= int(claims["exp"]):
        raise ValueError("JWT expired")

    return claims


def extract_bearer_token(auth_header: str) -> str:
    """Extract a bearer token from an Authorization header.

    Expected format:
    - "Bearer <token>"

    Raise ValueError when header is missing/malformed.
    """
    if not auth_header or not auth_header.strip():
        raise ValueError("Missing Authorization header")

    parts = auth_header.strip().split(None, 1)
    if len(parts) != 2:
        raise ValueError("Malformed Authorization header")

    scheme, token = parts
    if scheme.lower() != "bearer" or not token.strip():
        raise ValueError("Malformed bearer token")

    return token.strip()


def token_has_required_scopes(claims: dict, required_scopes: set[str]) -> bool:
    """Check whether token claims satisfy required OAuth scopes.

    Support either claim style:
    - scope: "space separated scopes"
    - scopes: ["scope:a", "scope:b"]

    Return True only when all required scopes are present.
    """
    if not required_scopes:
        return True

    available: set[str] = set()

    scope_str = claims.get("scope")
    if isinstance(scope_str, str):
        available.update(scope_str.split())

    scope_list = claims.get("scopes")
    if isinstance(scope_list, list):
        available.update(scope for scope in scope_list if isinstance(scope, str))

    return required_scopes.issubset(available)
