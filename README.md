# Week 4: Error Handling, Logging, and Basic Retries

## Learning Objectives
By the end of this lesson, you will:
- add helpful logs 
- control log verbosity with environment configuration
- use `logger.exception(...)` to preserve stack traces
- retry transient infrastructure failures safely
- ... all while keeping domain logic clean 

---

## Why This Week Matters

Up to Week 3, we focused on validating data and configuration early. That is necessary, but production issues still happen after startup.

Common examples:
- payload arrives with invalid values that our type validators don't catch
- database insert fails because of a temporary lock
- tests fail in CI with little context because logs are too sparse

The goal is to make failures obvious, actionable, and bounded.

---

## Logging You Can Actually Use

Use standard levels:
- `DEBUG` for deep troubleshooting
- `INFO` for normal successful flow
- `WARNING` for recoverable issues (like retries)
- `ERROR`/`CRITICAL` for terminal failures

Use a consistent format so local logs and CI logs are easy to scan:

`timestamp,level,msg`

In Python logging format terms:

`%(asctime)s,%(levelname)s,%(message)s`

Also, remember the difference between:
- `logger.error("...")` -> message only
- `logger.exception("...")` -> message plus traceback (inside `except`)

If you are catching an exception and re-raising it, `logger.exception(...)` is usually what you want.

---

## When Retries Help (And When They Don’t)

Retries are for failures that can change between attempts.

Good retry candidates:
- temporary database lock
- brief network timeout
- transient service unavailability

Bad retry candidates:
- invalid data shape
- failed regex validation
- missing required fields

Concrete example:
- If `site_id` fails a regex check now, retrying that exact same string five times will still fail five times.
- If DB insert fails due to a short lock, retrying may succeed on the next attempt.

So this week’s rule is simple:
- do **not** retry validation failures
- **do** retry persistence failures up to a small, fixed limit

We are keeping retries simple with a bounded attempt count (`max_retries`). In real systems, teams often add exponential backoff (wait a little longer before each retry) plus jitter to avoid synchronized retry storms.

---

## Golden Rules (So It Does Not Become a Swamp)

1. Validate early, outside retry loops.
   - If input/config is invalid, fail once, log once, and return the error.

2. Retry only the unstable I/O boundary.
   - Put retries around the DB write call, not around the whole function.

3. Keep `try/except` as narrow as possible.
   - Catch `ValidationError` around validation.
   - Catch runtime exceptions around persistence.

4. Log once per decision point.
   - `DEBUG`: start/context
   - `WARNING`: each retry attempt
   - `INFO`: success
   - `exception(...)`: terminal failure before re-raise

5. Re-raise after terminal failure.
   - Logging is observability, not recovery by itself.

If you follow these five rules, your code stays readable and your logs stay useful.

---

## Assignment

Implement Week 4 in the existing project.

### 1) Extend config in `src/config/settings.py`
- Add `log_level` to `Settings` with default `INFO`.
- Update `from_env()` to read `LOG_LEVEL` (default `INFO`).
- Validate allowed values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

### 2) Implement orchestration in `src/main.py`
- Implement `load_settings()`.
- Implement `build_logger(log_level, stream=None)`:
  - logger name: `oil_well_monitoring`
  - format: `%(asctime)s,%(levelname)s,%(message)s`
  - avoid duplicate handlers in repeated calls
- Implement `process_alert_event(..., max_retries=2)`:
  - validate with `Alert`
  - classify + persist using existing code
  - retry persistence failures up to `max_retries`
  - log retry attempts with `WARNING`
  - on validation failure: `logger.exception(...)` then re-raise
  - on final persistence failure: `logger.exception(...)` then re-raise
  - on success: log at `INFO`

### 3) Local debugging toggle in `.env`

Set:

```dotenv
LOG_LEVEL=DEBUG
```

Use this while debugging so debug lines appear. Tests should still pass with default `INFO` behavior.

---

## Testing

```bash
pytest tests/test_week4.py -v
pytest tests -v
```

---

## Success Criteria

- ✅ Week 1-4 tests pass
- ✅ logs follow `timestamp,level,msg`
- ✅ debug logs appear when `LOG_LEVEL=DEBUG`
- ✅ validation failures are logged with traceback and not retried
- ✅ persistence failures retry up to the limit, then log and raise

---

## Next Week Preview

Week 5 will look at authentication options, including API key auth and OAuth, and where each one fits.
