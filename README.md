# Week 4: Error Handling, Logging, and Basic Retries

## Learning Objectives
By the end of this lesson, you will:
- Add useful logs for success and failure paths
- Configure logging through environment variables
- Use `logger.exception(...)` to keep stack traces in logs
- Retry transient persistence failures in a controlled way
- Keep domain logic clean while orchestration handles runtime behavior

---

## 20-Minute Talk Plan

### 0:00-4:00 - Runtime failures you will hit
- Invalid payloads
- Temporary DB failures
- Why silent failures waste hours

### 4:00-8:00 - Logging essentials
- Levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Keep format standard: `timestamp,level,msg`
- `DEBUG` is opt-in

### 8:00-12:00 - `logger.error` vs `logger.exception`
- `logger.error(...)` for message-only failures
- `logger.exception(...)` inside `except` for traceback + context

### 12:00-16:00 - Simple retry strategy
- Retry only infra failures
- Do not retry validation failures
- Keep retries bounded (`max_retries`)

### 16:00-20:00 - Configuration and workflow
- Add `LOG_LEVEL` in config with default `INFO`
- Set local `.env` to `LOG_LEVEL=DEBUG` when debugging
- Tests should pass even when log level is not `DEBUG`

---

## 15-Minute Assignment Solve Plan

### 0:00-5:00 - Config + logger
1. Add `log_level` to `Settings`.
2. Read `LOG_LEVEL` from env (default `INFO`).
3. Build logger with `%(asctime)s,%(levelname)s,%(message)s`.

### 5:00-11:00 - Process flow with errors + retries
1. Validate input with `Alert`.
2. Classify and persist.
3. On persistence failure, retry up to `max_retries`.
4. Log retry attempts with `WARNING`.
5. On final failure, use `logger.exception(...)` and re-raise.
6. On validation failure, use `logger.exception(...)` and re-raise immediately.

### 11:00-15:00 - Verify behavior
1. Run Week 4 tests.
2. Run all tests.
3. Set `.env` to `LOG_LEVEL=DEBUG` and confirm debug lines appear.

---

## Your Assignment

Implement Week 4 in the existing project.

### In `src/config/settings.py`
1. Add `log_level` to `Settings` (default `INFO`).
2. Update `from_env()` to read `LOG_LEVEL` with default `INFO`.
3. Validate allowed values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

### In `src/main.py`
1. Implement `load_settings()`.
2. Implement `build_logger(log_level, stream=None)`.
   - Logger name: `oil_well_monitoring`
   - Format: `%(asctime)s,%(levelname)s,%(message)s`
3. Implement `process_alert_event(..., max_retries=2)`.
   - Validate with `Alert`
   - Persist via existing repository call
   - Retry persistence failures up to `max_retries`
   - Log each retry at `WARNING`
   - Use `logger.exception(...)` for validation failures and final runtime failure
   - Re-raise after logging

### In local `.env`
Add this during debugging:

```dotenv
LOG_LEVEL=DEBUG
```

This is part of the assignment: turn `DEBUG` on and verify debug logs appear. Unit tests should still pass with default `INFO` behavior.

---

## Testing

```bash
pytest tests/test_week4.py -v
pytest tests -v
```

---

## Success Criteria

- ✅ Week 1-4 tests pass
- ✅ Logs use `timestamp,level,msg` format
- ✅ `DEBUG` logs appear when `LOG_LEVEL=DEBUG`
- ✅ Validation failures are logged with `logger.exception(...)`
- ✅ Persistence failures retry, then log+raise when exhausted

---

## Next Week Preview

Week 5 will cover authentication basics: API key auth and OAuth, and where each fits in real systems.
