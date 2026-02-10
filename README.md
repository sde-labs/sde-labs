# Week 3: Environment Variables & Secrets

## Learning Objectives
By the end of this lesson, you will:
- Understand why secrets should never be hardcoded or committed
- Learn how environment variables separate code from configuration (local dev vs CI)
- Validate configuration early to fail fast (just like Week 2 input validation)
- Recognize the boundary between config validation and business logic (config is neither infra nor domain)

---

## The Problem with Week 2 Code

We validated data, but configuration is still implicit. That leads to brittle deployments and leaked secrets.

```python
# Hardcoded values or hidden assumptions
database_url = "alerts.db"          # ❌
api_token = "replace-me"            # ❌
```

**What happens?**
1. ✅ Code runs locally
2. ❌ Secrets end up in source control
3. ❌ Prod needs different config than dev/test
4. ❌ CI (GitHub Actions) doesn't have your laptop's `.env` or shell exports, so failures show up in CI first

---

## The Solution: Environment Variables

Environment variables keep config out of code. Validate them at startup so failures are immediate.

### Enter python-dotenv and gh-secrets
`python-dotenv` loads local `.env` values for development (never commit `.env`). In CI, use GitHub Secrets (`gh secret set -f .env` or UI) to provide the same variables.

---

## Example Pattern

```python
import os
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator

class Settings(BaseModel):
    env: str
    database_url: str
    api_token: str

    @classmethod
    def from_env(cls):
        load_dotenv()
        return cls(
            env=os.getenv("APP_ENV"),
            database_url=os.getenv("DATABASE_URL"),
            api_token=os.getenv("API_TOKEN"),
        )

    @field_validator("env")
    def validate_env(cls, v):
        if v not in {"dev", "test", "prod"}:
            raise ValueError("env must be one of: dev, test, prod")
        return v
```

---

## Understanding the Architecture

### Where Does Configuration Belong?

Configuration is not business logic. It sits at the boundary and should be validated before your domain logic runs.

- **Config validation**: Boundary/infrastructure concern - validate once at startup, then pass safe values inward
- **Business validation**: Domain concern - validate inputs and rules that exist even without deployment

 `APP_ENV` represents a whole slice of infrastructure.
If you run `dev`, you usually mean a full set of resources like `dev_lambda`, `dev_db`, `dev_gateway`.
If you run `stg`, you usually mean `stg_lambda`, `stg_db`, `stg_gateway`. Same code, different world.

---

## Testing Your Solution

### Run Tests Locally
```bash
pytest tests/test_week3.py -v  # Should pass after implementing config, and prior weeks should still pass
```

Local: use `.env` or exports. CI: set repo secrets. Missing secrets should fail fast.

### Expected Behavior

**Valid config (should work):**
```dotenv
APP_ENV=dev
DATABASE_URL=alerts.db
API_TOKEN=replace-me
```

**CI setup (GitHub Actions): set repo secrets using your preferred method**
UI: `Settings -> Secrets and variables -> Actions -> New repository secret`
CLI: `gh secret set -f .env`

---

## Real-World Connection

### Where You’ll Use This
- Deployments where config differs per environment
- CI systems (like GitHub Actions) injecting credentials at runtime

This week we only set the GH Secrets, and unit tests prove whether they exist.
In a full CI/CD pipeline, the next step is taking those same values and deploying them into cloud/local infrastructure (for example with Terraform or Ansible).

### Industry Standard
- Docker Compose: direct `.env` interpolation for service config
- GitHub Actions: `gh secret set -f .env` to import dotenv keys as secrets
- `python-dotenv`: direct `.env` loading in app startup
- 12-factor apps: config in environment, not in code

---

## Discussion Questions

**Production Scenario:** A developer accidentally checks in a `.env` file with a real API token. What could go wrong? How do you prevent it? How do you remediate it?

---

## Your Assignment

Implement the Week 3 config layer.

**In `src/config/settings.py`:**
1. Implement `from_env()` using `python-dotenv`.
2. Require `APP_ENV`, `DATABASE_URL`, `API_TOKEN`.
3. Validate:
   - `env` in `dev | test | prod`
   - `database_url` is non-empty and ends with `.db`
   - `api_token` is non-empty

**In `src/main.py`:**
- Implement `load_settings()` to return `Settings.from_env()`.

---

## Next Week Preview

Week 4 will introduce **error handling and logging**, so failures become visible and debuggable in production.

---

## Success Criteria

- ✅ All tests from this week and prior weeks pass
- ✅ Missing env vars fail fast
- ✅ Invalid config is rejected
- ✅ Valid config loads cleanly
