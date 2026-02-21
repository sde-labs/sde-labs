"""
Main application demonstrating clean architecture with validation.
"""
import logging

from pydantic import ValidationError

from src.config.settings import Settings
from src.domain.models import Alert
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

    TODO (Week 4): Return Settings.from_env().
    """
    raise NotImplementedError


def build_logger(log_level: str, stream=None) -> logging.Logger:
    """
    Build and return the application logger.

    TODO (Week 4):
    - create/get a logger named "oil_well_monitoring"
    - set the logger level from `log_level`
    - attach one StreamHandler (default stream if stream is None)
    - set formatter to: %(asctime)s,%(levelname)s,%(message)s
    - avoid duplicate handlers across repeated calls in tests
    """
    raise NotImplementedError


def process_alert_event(conn, logger: logging.Logger, timestamp: str, site_id: str,
                        alert_type: str, latitude: float, longitude: float,
                        max_retries: int = 2) -> Alert:
    """
    Validate, classify, persist, and log one alert.

    TODO (Week 4):
    - log debug context before processing
    - build Alert to validate input
    - classify and persist alert
    - retry persistence failures up to `max_retries`
    - log each retry with WARNING
    - log success at INFO
    - on ValidationError use logger.exception(...) then re-raise
    - after final failed retry use logger.exception(...) then re-raise
    """
    raise NotImplementedError
