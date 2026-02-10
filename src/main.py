"""
Main application demonstrating clean architecture with validation.
"""
from src.config.settings import Settings
from src.domain.processor import classify_alert
from src.infrastructure.database import get_connection, initialize_database
from src.infrastructure.repositories import insert_alert


def process_alert_reading(conn, timestamp: str, site_id: str, alert_type: str,
                          latitude: float, longitude: float):
    """
    Process and store alert data with severity classification.
    
    Week 2 Note: This function now benefits from Pydantic validation in the
    Alert model. Invalid data (e.g., latitude > 90) will raise ValidationError
    before reaching this point if you use the Alert model to validate inputs.
    """
    # Step 1: Classify alert (Domain layer - pure logic, no I/O)
    severity = classify_alert(alert_type)
    
    # Step 2: Persist to database (Infrastructure layer - I/O)
    insert_alert(conn, timestamp, site_id, alert_type, severity, latitude, longitude)
    
    print(f"Alert recorded with severity: {severity}")


def load_settings():
    """
    Load application settings from environment.

    TODO (Week 3): Replace NotImplementedError with Settings.from_env().
    This should fail fast when required config is missing in local `.env` or CI env vars.
    """
    raise NotImplementedError
