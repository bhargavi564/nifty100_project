import sqlite3
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()
DB_PATH = Path(__file__).resolve().parents[3] / "data" / "nifty100.db"

@router.get("/market-cap/{ticker}")
def get_valuation(ticker: str):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT year, price_to_earnings as pe, price_to_book as pb, 
               ev_ebitda, dividend_yield_pct 
        FROM financial_ratios 
        WHERE company_id = ? AND year BETWEEN 2019 AND 2024
        ORDER BY year ASC
    """, (ticker,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]