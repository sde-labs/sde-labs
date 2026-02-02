"""
Domain layer - pure business logic with no I/O operations
"""


def classify_alert(alert_type: str) -> str:
    """
    Takes an alert type and returns its severity level.
    
    Business rules:
    - LEAK: CRITICAL
    - BLOCKAGE: CRITICAL
    - PRESSURE: MODERATE
    - TEMPERATURE: MODERATE
    - ACOUSTIC: MODERATE
    
    Args:
        alert_type: One of PRESSURE, TEMPERATURE, LEAK, ACOUSTIC, BLOCKAGE
        
    Returns:
        "CRITICAL" or "MODERATE"
    """
    if alert_type in ["LEAK", "BLOCKAGE"]:
        return "CRITICAL"
    return "MODERATE"
