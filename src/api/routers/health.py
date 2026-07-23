import time
import sqlite3
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()

# Resolve database path
BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "data" / "nifty100.db"

# Track server boot time
START_TIME = time.time()

def get_db_connection():
    """Establish a SQLite connection."""
    conn = sqlite3.connect(str(DB_PATH))
    return conn

@router.get("/health")
def health_check():
    """Returns server status, uptime, and database row counts."""
    uptime_seconds = time.time() - START_TIME
    db_row_counts = {}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Dynamically fetch all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Count rows for each table
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            db_row_counts[table] = cursor.fetchone()[0]
            
        conn.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime_seconds": round(uptime_seconds, 2),
        "database_status": db_status,
        "db_row_counts": db_row_counts
    }