"""
Tests for Week 1 assignment
"""
import sys
import os
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.domain.processor import classify_alert
from src.infrastructure.database import get_connection, initialize_database
from src.infrastructure.repositories import insert_alert, get_all_alerts


def test_classify_alert_critical():
    """Test that LEAK and BLOCKAGE are classified as CRITICAL."""
    assert classify_alert("LEAK") == "CRITICAL"
    assert classify_alert("BLOCKAGE") == "CRITICAL"


def test_classify_alert_moderate():
    """Test that other alert types are classified as MODERATE."""
    assert classify_alert("PRESSURE") == "MODERATE"
    assert classify_alert("TEMPERATURE") == "MODERATE"
    assert classify_alert("ACOUSTIC") == "MODERATE"


def test_insert_alert():
    """Test that alerts can be inserted into the database."""
    # Use in-memory database for testing
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)
    
    # Insert a test alert
    insert_alert(
        conn,
        timestamp="2024-01-26T10:00:00Z",
        site_id="TEST_SITE",
        alert_type="LEAK",
        severity="CRITICAL",
        latitude=29.7604,
        longitude=-95.3698
    )
    
    # Verify it was inserted
    alerts = get_all_alerts(conn)
    assert len(alerts) == 1
    assert alerts[0][2] == "LEAK"  # alert_type
    assert alerts[0][3] == "CRITICAL"  # severity
    
    conn.close()


def test_domain_infrastructure_separation():
    """
    Test that domain layer doesn't import from infrastructure.
    This is a critical architectural constraint.
    """
    import src.domain.processor as domain_module
    import inspect
    
    source = inspect.getsource(domain_module)
    
    # Check that domain doesn't import from infrastructure
    assert "from infrastructure" not in source and "from src.infrastructure" not in source, \
        "Domain layer should not import from infrastructure layer"
    assert "import infrastructure" not in source and "import src.infrastructure" not in source, \
        "Domain layer should not import from infrastructure layer"
