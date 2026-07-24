import sqlite3
import statistics
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()
DB_PATH = Path(__file__).resolve().parents[3] / "data" / "nifty100.db"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/sectors")
def get_sectors():
    """Returns all 11 sectors with company counts and median KPIs."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.broad_sector as sector, f.return_on_equity_pct, f.price_to_earnings, f.debt_to_equity
        FROM companies c
        JOIN (SELECT * FROM financial_ratios GROUP BY company_id HAVING MAX(year)) f 
        ON c.id = f.company_id
    """)
    rows = cursor.fetchall()
    conn.close()
    
    sectors_data = {}
    for row in rows:
        sec = row["sector"]
        if sec not in sectors_data:
            sectors_data[sec] = {"roe": [], "pe": [], "de": [], "count": 0}
        
        sectors_data[sec]["count"] += 1
        if row["return_on_equity_pct"] is not None: sectors_data[sec]["roe"].append(row["return_on_equity_pct"])
        if row["price_to_earnings"] is not None: sectors_data[sec]["pe"].append(row["price_to_earnings"])
        if row["debt_to_equity"] is not None: sectors_data[sec]["de"].append(row["debt_to_equity"])
        
    results = []
    for sec, data in sectors_data.items():
        results.append({
            "sector": sec,
            "company_count": data["count"],
            "median_roe": statistics.median(data["roe"]) if data["roe"] else None,
            "median_pe": statistics.median(data["pe"]) if data["pe"] else None,
            "median_de": statistics.median(data["de"]) if data["de"] else None
        })
    return results

@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.company_name, f.* 
        FROM companies c
        JOIN (SELECT * FROM financial_ratios GROUP BY company_id HAVING MAX(year)) f ON c.id = f.company_id
        WHERE c.broad_sector = ?
    """, (sector,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail="Unknown sector or no companies found.")
    return [dict(r) for r in rows]