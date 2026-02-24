# Week 5: Testing That Catches Real Bugs

## Learning Objectives
By the end of this lesson, you will:
- write focused tests for happy paths and failure paths
- test retries and logging behavior without flaky sleeps
- use fixtures, parametrization, and monkeypatch in practical ways
- keep tests readable and deterministic

---

## Why This Week Matters

By Week 4 we have validation, logging, and retries. That gives us better runtime behavior, but we still need protection against regressions.

Good tests are not about chasing coverage numbers. They protect behavior that matters.

In this project, the most important behaviors are:
- bad config is rejected
- invalid alerts fail fast
- transient persistence errors retry
- terminal failures are logged and raised

---

## What To Test In This Repo

### 1) Config behavior
`Settings.from_env()` should:
- load valid values
- fail when required vars are missing
- reject invalid values
- default optional values like `LOG_LEVEL`

Example: if someone removes the `.db` validation, your test should fail right away.

### 2) Logger behavior
`build_logger()` should:
- use `timestamp,level,msg` format
- show debug lines only when level is `DEBUG`

### 3) Orchestration behavior
`process_alert_event()` should:
- validate and persist on happy path
- not retry validation failures
- retry transient persistence failures
- log terminal failures and re-raise

Example: retrying a bad `alert_type` is useless, retrying a temporary DB failure can help.

---

## Golden Rules

1. Test behavior, not implementation details.
2. Keep each test focused on one outcome.
3. Avoid nondeterminism (no sleeps, no network).
4. Use monkeypatch to simulate failures deterministically.
5. If production code re-raises exceptions, tests should assert that too.

If a test passes randomly, it is not done yet.

---

## Assignment

Implement the Week 5 tests.

### In `tests/test_week5.py`
Complete the TODO tests so they verify all key Week 4 behaviors.

You must include:
- at least one parametrized test (`@pytest.mark.parametrize`)
- at least one fixture (`@pytest.fixture`)
- at least one monkeypatch-based failure simulation

Keep each test small and explicit.

Expected focus areas:
- config validation and defaults
- logger level + format behavior
- retry semantics
- failure logging + exception re-raise

---

## Testing

```bash
pytest tests/test_week5.py -v
pytest tests -v
```

---

## Success Criteria

- ✅ Prior week tests still pass
- ✅ Week 5 tests are deterministic and meaningful
- ✅ Retry tests verify the right failures are retried
- ✅ Failure path tests assert both logs and raised exceptions

---

## Next Week Preview

Week 6 will look at authentication options, including API key auth and OAuth, and where each one fits.
