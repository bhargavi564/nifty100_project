import sqlite3
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()
DB_PATH = Path(__file__).resolve().parents[3] / "data" / "nifty100.db"

@router.get("/companies/{ticker}/documents")
def get_company_documents(ticker: str):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE company_id = ?", (ticker,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        doc = dict(r)
        # Determine validity: basic check if URL exists and starts with http
        doc["is_url_valid"] = bool(doc.get("url") and doc["url"].startswith("http"))
        results.append(doc)
    return results