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

    Load and validate settings.
    """
    return Settings.from_env()


def build_logger(log_level: str, stream=None) -> logging.Logger:
    logger = logging.getLogger("oil_well_monitoring")
    logger.setLevel(log_level.upper())
    logger.propagate = False

    logger.handlers.clear()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s,%(levelname)s,%(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    logger.addHandler(handler)

    return logger


def process_alert_event(conn, logger: logging.Logger, timestamp: str, site_id: str,
                        alert_type: str, latitude: float, longitude: float,
                        max_retries: int = 2) -> Alert:
    logger.debug("processing_alert site_id=%s alert_type=%s", site_id, alert_type)

    try:
        alert = Alert(
            timestamp=timestamp,
            site_id=site_id,
            alert_type=alert_type,
            severity="",
            latitude=latitude,
            longitude=longitude,
        )
    except ValidationError:
        logger.exception("validation_failed")
        raise

    alert.severity = classify_alert(alert.alert_type)

    for attempt in range(max_retries + 1):
        try:
            insert_alert(
                conn,
                alert.timestamp,
                alert.site_id,
                alert.alert_type,
                alert.severity,
                alert.latitude,
                alert.longitude,
            )
            logger.info("alert_recorded")
            return alert
        except Exception:
            if attempt < max_retries:
                logger.warning(
                    "retrying_persist attempt=%s max_retries=%s",
                    attempt + 1,
                    max_retries,
                )
                continue

            logger.exception("alert_processing_failed")
            raise

    raise RuntimeError("unreachable")
