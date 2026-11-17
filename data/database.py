import sqlite3
import os
import sys
from pathlib import Path
from typing import Optional

if getattr(sys, "frozen", False):
    app_data = Path(
        os.environ.get(
            "LOCALAPPDATA",
            str(Path.home() / "AppData" / "Local")
        )
    )
    DB_DIR = app_data / "AcoustiGuard"
else:
    DB_DIR = Path(__file__).resolve().parent.parent

DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "acoustiguard.db"



def get_connection():
    """Get a connection to the AcoustiGuard database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the AcoustiGuard database with all required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Scans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date TEXT NOT NULL,
            scan_time TEXT NOT NULL,
            duration_seconds REAL NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            masking_enabled INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (risk_score >= 0 AND risk_score <= 100),
            CHECK (risk_level IN ('Low', 'Medium', 'High', 'Critical'))
        )
    """)
    
    # Acoustic features table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acoustic_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            rms_energy REAL,
            spectral_centroid REAL,
            spectral_bandwidth REAL,
            spectral_rolloff REAL,
            zero_crossing_rate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
        )
    """)
    
    # Recommendations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            recommendation_text TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_date ON scans(scan_date, scan_time DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_scan ON recommendations(scan_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_scan ON acoustic_features(scan_id)")
    
    # Insert default settings
    default_settings = [
        ('microphone_device', 'default'),
        ('microphone_sensitivity', '60'),
        ('enable_alerts', 'true'),
        ('enable_alert_sound', 'true'),
        ('history_retention_days', '30'),
        ('masking_default_volume', '65'),
    ]
    
    for key, value in default_settings:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
    
    conn.commit()
    conn.close()
    
    print(f"OK: Database initialized: {DB_PATH}")


def get_database_stats():
    """Get statistics about the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM scans")
    total_scans = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM scans WHERE created_at >= datetime('now', '-7 days')")
    recent_scans = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM settings")
    total_settings = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_scans': total_scans,
        'recent_scans': recent_scans,
        'total_settings': total_settings,
        'database_path': str(DB_PATH),
    }


if __name__ == "__main__":
    init_database()
    import json
    print(json.dumps(get_database_stats(), indent=2))
