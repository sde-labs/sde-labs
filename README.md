# Week 6: Practical Auth - Basic, JWT, and OAuth Scopes

## Learning Objectives
By the end of this lesson, you will:
- parse and verify Basic auth safely
- issue and verify HS256 JWTs with expiration
- extract bearer tokens and enforce OAuth-style scopes
- avoid common auth pitfalls in small Python services

---

## Why This Week Matters

Most security incidents are not caused by advanced crypto attacks. They happen because simple auth details are inconsistent or skipped.

Typical examples:
- accepting malformed `Authorization` headers
- comparing secrets with normal `==` instead of constant-time checks
- trusting JWT payloads without verifying signature or `exp`
- checking for "some scope" instead of all required scopes

This week is about building guardrails that are small, boring, and dependable.

---

## Three Auth Modes, One Mental Model

### 1) Basic Auth (credentials per request)
Good for internal tools and quick admin endpoints.

Use it correctly:
- parse `Basic <base64(username:password)>`
- handle decode errors as auth failures (not 500s)
- compare credentials with `hmac.compare_digest`

### 2) JWT (stateless signed token)
Good when you want a signed claim set passed between services.

Minimum checks:
- token has 3 segments
- signature matches HS256 secret
- `exp` exists and is still valid

### 3) OAuth-style scopes (authorization)
Auth says *who*. Scopes say *what they can do*.

Keep authorization explicit:
- require all scopes needed for an action
- support common claim styles (`scope` string, `scopes` list)

---

## Assignment

Implement Week 6 auth helpers in `src/security/auth.py`.

### 1) Basic auth functions
Implement:
- `parse_basic_auth_header(auth_header)`
- `verify_basic_credentials(auth_header, expected_username, expected_password)`

### 2) JWT functions
Implement:
- `create_hs256_jwt(subject, secret, expires_in_seconds=3600, scopes=None, now=None)`
- `verify_hs256_jwt(token, secret, now=None)`

Implementation notes:
- use URL-safe base64 segments without padding
- sign with HMAC-SHA256
- treat invalid structure/signature/expiration as `ValueError`

### 3) OAuth helpers
Implement:
- `extract_bearer_token(auth_header)`
- `token_has_required_scopes(claims, required_scopes)`

---

## Useful Idioms (Keep These)

1. Normalize input before checks.
   - Example: trim header value once, then parse.

2. Fail closed.
   - If token format is odd or claims are missing, reject.

3. Keep time deterministic in tests.
   - Accept `now` as an argument instead of calling `datetime.now()` directly.

4. Separate authentication from authorization.
   - Verify token first, then check required scopes.

5. Return booleans for allow/deny decisions, raise only for malformed/invalid auth artifacts.

---

## Testing

```bash
pytest tests/test_week6.py -v
pytest tests -v
```

---

## Success Criteria

- ✅ Week 1-5 tests still pass
- ✅ Basic auth parsing handles malformed input safely
- ✅ JWT verification rejects tampered or expired tokens
- ✅ Scope checks enforce least privilege (all required scopes)

---

## Next Week Preview

Week 7 will focus on hardening and observability: rate limits, audit logs, and secure failure responses.
