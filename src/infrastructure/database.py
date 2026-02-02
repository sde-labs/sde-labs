"""
Infrastructure layer - database connection management
"""
import sqlite3


def get_connection(db_path: str = "oil_well_monitoring.db"):
    """Creates and returns a database connection."""
    conn = sqlite3.connect(db_path)
    return conn


def initialize_database(conn):
    """Creates tables if they don't exist."""
    cursor = conn.cursor()
    
    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            timestamp TEXT NOT NULL,
            site_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)
    
    conn.commit()
