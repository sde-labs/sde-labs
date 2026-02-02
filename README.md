# Week 2: Type Validation with Pydantic

## Learning Objectives
By the end of this lesson, you will:
- Understand why validation at boundaries prevents bugs
- Learn to use Pydantic for data validation
- Enforce business rules through type constraints
- Recognize the difference between validation and business logic

---

## The Problem with Week 1 Code

In Week 1, we built a clean architecture with separated Domain and Infrastructure layers. **But there's a critical flaw:**

```python
# This code will happily accept garbage data!
process_alert_reading(
    conn,
    timestamp="2024-99-99T99:99:99Z", # ❌
    site_id="SITE_001",
    alert_type="RAINING_UNICORNS",  # ❌
    latitude=999.9,              # ❌
    longitude=-999.9             # ❌
)
```

**What happens?**
1. ✅ Code runs without errors
2. ❌ Invalid data gets stored in the database
3. ❌ Downstream systems fail when they encounter bad data
4. ❌ You discover the problem hours or days later

---

## The Solution: Validate at Boundaries

**Validate data as soon as it enters your system** using type validation.

### Enter Pydantic

Pydantic is Python's industry-standard library for data validation. It:
- ✅ Validates data types automatically
- ✅ Enforces custom business rules
- ✅ Raises clear errors when data is invalid
- ✅ Integrates seamlessly with type hints

---

## Your Assignment

You'll harden the Week 1 code by adding Pydantic validation to the `Alert` model.

### What You Need to Do

**In `domain/models.py`**: Add three validators to the `Alert` model

The file already has TODOs marked. You need to implement:

1. **Latitude Validator**
   - Must be between -90 and 90
   - Raise `ValueError` with a clear message if invalid

2. **Longitude Validator**
   - Must be between -180 and 180
   - Raise `ValueError` with a clear message if invalid

3. **Alert Type Validator**
   - Must be one of: `LEAK`, `BLOCKAGE`, `PRESSURE`, `TEMPERATURE`, `ACOUSTIC`
   - Raise `ValueError` listing valid types if invalid

4. **Bonus: Timestamp Validator**

### Example Validator Pattern

Here's the pattern for Pydantic validators:

```python
from pydantic import BaseModel, field_validator

class MyModel(BaseModel):
    my_field: float
    
    @field_validator('my_field')
    def validate_my_field(cls, v):
        if v < 0:
            raise ValueError('my_field must be positive')
        return v
```

**Key points:**
- Use the `@field_validator('field_name')` decorator
- Method signature: `def method_name(cls, v)`
- Raise `ValueError` with descriptive message
- Return the value if valid

---

## Understanding the Architecture

### Where Does Validation Belong? - Revistting Week 1

**Question:** Is validation part of the Domain layer or Infrastructure layer?

**Answer:** It depends on the *type* of validation.

**Domain Validation (Business Rules):**
- Example: "Latitude must be -90 to 90" ← This is a fact about Earth
- Example: "Alert types are LEAK, BLOCKAGE, etc." ← This is a business domain concept
- **These belong in Domain models** ✅

**Infrastructure Validation (I/O Constraints):**
- Example: "JSON must be valid UTF-8"
- Example: "Request body cannot exceed 1MB"
- **These belong in Infrastructure** ✅

For Week 2, all our validators are **domain rules**, so they go in `domain/models.py`.

---

## Testing Your Solution

### Run Tests Locally
```bash
pytest tests/test_week1.py -v  # Should still pass
pytest tests/test_week2.py -v  # Should pass after implementing validators
```

### Expected Behavior

**Valid data (should work):**
```python
alert = Alert(
    timestamp="2024-01-26T10:00:00Z",
    site_id="SITE_001",
    alert_type="LEAK",
    severity="CRITICAL",
    latitude=29.7604,
    longitude=-95.3698
)
print(alert)  # ✅ Works!
```

**Invalid data (should raise ValidationError):**
```python
from pydantic import ValidationError

try:
    alert = Alert(
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_001",
        alert_type="LEAK",
        severity="CRITICAL",
        latitude=999.9,  # ❌ Invalid
        longitude=-95.3698
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Validation failed: 1 validation error for Alert
    # latitude
    #   Value error, latitude must be between -90 and 90
```

---

## Real-World Connection

### Where You'll Use This

**Data Engineering Pipelines:**
- Validate incoming data from APIs, Kafka, or S3 before processing
- Catch schema changes early before they break downstream jobs
- Example: "This JSON from the vendor API looks weird..."
- Ensure data quality before loading into data warehouse

### Industry Standard

**Pydantic is used in:**
- Notable companies including Netflix, Microsoft, AWS, Uber.
- FastAPI 
- Data pipeline tools (Dagster, Prefect)
- ML model serving (validating inference inputs)

---

## Discussion Questions

**Production Scenario:** You're ingesting oil well sensor data from 10,000 wells via Kafka. One well starts sending `latitude=null`. Without validation, what breaks? With validation, what happens?

---

## Next Week Preview

Week 3 will introduce **error handling and logging**. You'll learn how to gracefully handle validation failures, log them properly, and ensure your pipeline is observable in production.

---

## Success Criteria

- ✅ All tests from this week and prior weeks pass (100 pts)
  - ✅ Invalid latitude/longitude are rejected 
  - ✅ Invalid alert types are rejected
  - ✅ Valid boundary values are accepted

