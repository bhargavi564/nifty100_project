import os
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 1. Generate Mock peer_groups.xlsx
peers_data = {
    "company_id": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "ITC", "HUL", "BHARTIARTL", "SBIN", "TATASTEEL"],
    "peer_group_name": ["Energy", "IT Services", "IT Services", "Banking", "Banking", "FMCG", "FMCG", "Telecom", "Banking", "Metals"]
}
df_peers = pd.DataFrame(peers_data)
excel_path = DATA_DIR / "peer_groups.xlsx"
df_peers.to_excel(excel_path, index=False)
print(f"[SUCCESS] Mock Excel created at: {excel_path}")

# 2. Generate Mock nifty100.db with matching metrics
db_path = DATA_DIR / "nifty100.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table matching our SQL query in peer.py
cursor.execute("""
    CREATE TABLE IF NOT EXISTS company_metrics (
        company_id TEXT,
        metric TEXT,
        value REAL,
        year INTEGER
    )
""")

# Insert mock values for peer calculation comparison
mock_metrics = [
    # IT Services Peer Group
    ("TCS", "ROE", 38.2, 2026),
    ("TCS", "D/E", 0.02, 2026),
    ("TCS", "FCF", 32000.0, 2026),
    ("INFY", "ROE", 29.1, 2026),
    ("INFY", "D/E", 0.00, 2026),
    ("INFY", "FCF", 21000.0, 2026),
    
    # Banking Peer Group
    ("HDFCBANK", "ROE", 16.2, 2026),
    ("HDFCBANK", "D/E", 0.85, 2026),
    ("ICICIBANK", "ROE", 18.1, 2026),
    ("ICICIBANK", "D/E", 0.78, 2026),
    ("SBIN", "ROE", 15.0, 2026),
    ("SBIN", "D/E", 1.20, 2026),
    
    # FMCG Peer Group
    ("ITC", "ROE", 25.4, 2026),
    ("ITC", "D/E", 0.00, 2026),
    ("HUL", "ROE", 18.5, 2026),
    ("HUL", "D/E", 0.05, 2026),
]

cursor.executemany("INSERT INTO company_metrics VALUES (?, ?, ?, ?)", mock_metrics)
conn.commit()
conn.close()
print(f"[SUCCESS] Mock SQLite DB created at: {db_path}")