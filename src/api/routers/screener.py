import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()
DB_PATH = Path(__file__).resolve().parents[3] / "data" / "nifty100.db"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/screener")
def run_screener(
    min_roe: float = Query(None), max_de: float = Query(None),
    min_fcf: float = Query(None), sector: str = Query(None),
    min_rev_cagr: float = Query(None, alias="min_rev_cagr_5yr"), 
    min_pat_cagr: float = Query(None, alias="min_pat_cagr_5yr"),
    max_pe: float = Query(None)
):
    """Returns a ranked list of companies matching the filter criteria."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        query = """
            SELECT c.id, c.company_name, c.broad_sector, f.return_on_equity_pct, 
                   f.debt_to_equity, f.free_cash_flow, f.revenue_cagr_5yr, 
                   f.pat_cagr_5yr, f.price_to_earnings
            FROM companies c
            JOIN (
                SELECT *, ROW_NUMBER() OVER(PARTITION BY company_id ORDER BY year DESC) as rn
                FROM financial_ratios
            ) f ON c.id = f.company_id AND f.rn = 1
            WHERE 1=1
        """
        params = []
        
        if min_roe is not None: query += " AND f.return_on_equity_pct >= ?"; params.append(min_roe)
        if max_de is not None: query += " AND f.debt_to_equity <= ?"; params.append(max_de)
        if min_fcf is not None: query += " AND f.free_cash_flow >= ?"; params.append(min_fcf)
        if sector: query += " AND c.broad_sector = ?"; params.append(sector)
        if min_rev_cagr is not None: query += " AND f.revenue_cagr_5yr >= ?"; params.append(min_rev_cagr)
        if min_pat_cagr is not None: query += " AND f.pat_cagr_5yr >= ?"; params.append(min_pat_cagr)
        if max_pe is not None: query += " AND f.price_to_earnings <= ?"; params.append(max_pe)
            
        query += " ORDER BY f.return_on_equity_pct DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid parameter values provided.")
    finally:
        conn.close()