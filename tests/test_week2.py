"""
Tests for Week 2 assignment - Pydantic Validation
"""
import sys
import os
import pytest
from pydantic import ValidationError

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.domain.models import Alert


def test_valid_alert_accepted():
    """Test that valid alert data is accepted."""
    alert = Alert(
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_001",
        alert_type="LEAK",
        severity="CRITICAL",
        latitude=29.7604,
        longitude=-95.3698
    )
    assert alert.latitude == 29.7604
    assert alert.longitude == -95.3698
    assert alert.alert_type == "LEAK"


def test_invalid_latitude_rejected():
    """Test that latitude outside -90 to 90 range is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Alert(
            timestamp="2024-01-26T10:00:00Z",
            site_id="SITE_001",
            alert_type="LEAK",
            severity="CRITICAL",
            latitude=999.9,  # Invalid: way outside range
            longitude=-95.3698
        )
    
    # Verify the error mentions latitude
    error_str = str(exc_info.value)
    assert "latitude" in error_str.lower()


def test_invalid_longitude_rejected():
    """Test that longitude outside -180 to 180 range is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Alert(
            timestamp="2024-01-26T10:00:00Z",
            site_id="SITE_001",
            alert_type="LEAK",
            severity="CRITICAL",
            latitude=29.7604,
            longitude=999.9  # Invalid: way outside range
        )
    
    # Verify the error mentions longitude
    error_str = str(exc_info.value)
    assert "longitude" in error_str.lower()


def test_invalid_alert_type_rejected():
    """Test that invalid alert types are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Alert(
            timestamp="2024-01-26T10:00:00Z",
            site_id="SITE_001",
            alert_type="INVALID_TYPE",  # Not in the allowed list
            severity="CRITICAL",
            latitude=29.7604,
            longitude=-95.3698
        )
    
    # Verify the error mentions alert_type
    error_str = str(exc_info.value)
    assert "alert_type" in error_str.lower()


def test_boundary_values_accepted():
    """Test that boundary values for lat/lon are accepted."""
    # Test max latitude
    alert1 = Alert(
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_001",
        alert_type="PRESSURE",
        severity="MODERATE",
        latitude=90.0,  # Max valid
        longitude=0.0
    )
    assert alert1.latitude == 90.0
    
    # Test min latitude
    alert2 = Alert(
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_002",
        alert_type="TEMPERATURE",
        severity="MODERATE",
        latitude=-90.0,  # Min valid
        longitude=0.0
    )
    assert alert2.latitude == -90.0
    
    # Test max longitude
    alert3 = Alert(
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_003",
        alert_type="ACOUSTIC",
        severity="MODERATE",
        latitude=0.0,
        longitude=180.0  # Max valid
    )
    assert alert3.longitude == 180.0
    
    # Test min longitude
    alert4 = Alert(
        timestamp="2024-01-26T10:00:00Z",
        site_id="SITE_004",
        alert_type="BLOCKAGE",
        severity="CRITICAL",
        latitude=0.0,
        longitude=-180.0  # Min valid
    )
    assert alert4.longitude == -180.0


def test_all_valid_alert_types():
    """Test that all valid alert types are accepted."""
    valid_types = ["LEAK", "BLOCKAGE", "PRESSURE", "TEMPERATURE", "ACOUSTIC"]
    
    for alert_type in valid_types:
        alert = Alert(
            timestamp="2024-01-26T10:00:00Z",
            site_id="SITE_001",
            alert_type=alert_type,
            severity="CRITICAL" if alert_type in ["LEAK", "BLOCKAGE"] else "MODERATE",
            latitude=29.7604,
            longitude=-95.3698
        )
        assert alert.alert_type == alert_type
