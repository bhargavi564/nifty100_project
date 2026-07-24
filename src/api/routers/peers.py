import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()
DB_PATH = Path(__file__).resolve().parents[3] / "data" / "nifty100.db"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/peers/{group_name}")
def get_peer_group(group_name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM peer_percentiles WHERE peer_group_name = ?", (group_name,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail="Unknown peer group.")
    return [dict(r) for r in rows]

@router.get("/companies/{ticker}/peers/compare")
def compare_peers(ticker: str):
    """Returns radar data comparing a company against its peer group average."""
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Identify peer group
    cursor.execute("SELECT peer_group_name FROM peer_percentiles WHERE company_id = ?", (ticker,))
    group = cursor.fetchone()
    if not group:
        conn.close()
        raise HTTPException(status_code=404, detail="Company peer group not found.")
        
    group_name = group["peer_group_name"]
    
    # 2. Get company data & group average
    cursor.execute("""
        SELECT company_id, return_on_equity_pct, operating_profit_margin_pct, net_profit_margin_pct,
               revenue_cagr_5yr, pat_cagr_5yr, debt_to_equity, interest_coverage, price_to_earnings
        FROM financial_ratios f
        JOIN peer_percentiles p ON f.company_id = p.company_id
        WHERE p.peer_group_name = ? AND f.year = (SELECT MAX(year) FROM financial_ratios)
    """, (group_name,))
    
    all_peers = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    target_company = next((p for p in all_peers if p["company_id"] == ticker), None)
    
    # Calculate averages
    averages = {}
    metrics = ["return_on_equity_pct", "operating_profit_margin_pct", "net_profit_margin_pct", 
               "revenue_cagr_5yr", "pat_cagr_5yr", "debt_to_equity", "interest_coverage", "price_to_earnings"]
               
    for m in metrics:
        valid_vals = [p[m] for p in all_peers if p[m] is not None]
        averages[m] = sum(valid_vals) / len(valid_vals) if valid_vals else None

    return {
        "company": target_company,
        "peer_group_average": averages,
        "benchmark_company": all_peers[0] if all_peers else None # Simplified benchmark selection
    }