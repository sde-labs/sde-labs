"""
Infrastructure layer - data access operations
"""


def insert_alert(conn, timestamp: str, site_id: str, alert_type: str, 
                severity: str, latitude: float, longitude: float):
    """
    Persists alert data to the database.
    
    Args:
        conn: SQLite connection
        timestamp: When the alert occurred
        site_id: Which site generated the alert
        alert_type: Type of alert (PRESSURE, TEMPERATURE, etc.)
        severity: CRITICAL or MODERATE
        latitude: Site latitude
        longitude: Site longitude
    """
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO alerts (timestamp, site_id, alert_type, severity, latitude, longitude) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (timestamp, site_id, alert_type, severity, latitude, longitude)
    )
    conn.commit()


def get_all_alerts(conn):
    """Retrieves all alerts from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts")
    return cursor.fetchall()
