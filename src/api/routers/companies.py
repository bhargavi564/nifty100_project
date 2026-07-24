import sqlite3
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter()

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
TEARSHEETS_DIR = BASE_DIR / "reports" / "tearsheets"

def get_db():
    """Helper to establish DB connection and return dictionary-like rows."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/companies")
def get_companies(
    sector: Optional[str] = None,
    market_cap_category: Optional[str] = None,
    search: Optional[str] = None
):
    """Returns a list of all companies with latest ROE, supporting optional filters."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Use c.* to safely fetch available columns without hardcoding potentially missing ones
        query = """
            SELECT c.id as id, c.company_name, c.*,
                   f.return_on_equity_pct as roe_pct, NULL as roce_pct
            FROM companies c
            LEFT JOIN (
                SELECT company_id, return_on_equity_pct,
                       ROW_NUMBER() OVER(PARTITION BY company_id ORDER BY year DESC) as rn
                FROM financial_ratios
            ) f ON c.id = f.company_id AND f.rn = 1
            WHERE 1=1
        """
        params = []
        
        # Only apply 'search' filter in SQL because 'company_name' and 'id' are guaranteed to exist
        if search:
            query += " AND (c.company_name LIKE ? OR c.id LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert DB rows to standard Python dictionaries
        results = [dict(row) for row in rows]
        
        # Apply the remaining filters in Python to prevent SQLite "no such column" crashes
        if sector:
            results = [r for r in results if r.get("broad_sector") == sector or r.get("sector") == sector]
        if market_cap_category:
            results = [r for r in results if r.get("market_cap_category") == market_cap_category]
            
        return results
    finally:
        conn.close()

@router.get("/companies/{ticker}")
def get_company_profile(ticker: str):
    """Returns full company profile including latest year KPIs."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM companies WHERE id = ?", (ticker,))
        company = cursor.fetchone()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company ticker not found")
            
        cursor.execute("SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year DESC LIMIT 1", (ticker,))
        latest_kpis = cursor.fetchone()
        
        result = dict(company)
        result["latest_kpis"] = dict(latest_kpis) if latest_kpis else {}
        return result
    finally:
        conn.close()

def fetch_history(table: str, ticker: str, from_year: Optional[str], to_year: Optional[str]):
    """Generic helper to fetch historical statement arrays."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table} WHERE company_id = ?"
        params = [ticker]
        
        if from_year:
            query += " AND year >= ?"
            params.append(from_year)
        if to_year:
            query += " AND year <= ?"
            params.append(to_year)
            
        query += " ORDER BY year ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@router.get("/companies/{ticker}/pl")
def get_profit_and_loss(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None):
    """Returns Profit & Loss history array."""
    return fetch_history("profitandloss", ticker, from_year, to_year)

@router.get("/companies/{ticker}/bs")
def get_balance_sheet(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None):
    """Returns Balance Sheet history array."""
    return fetch_history("balancesheet", ticker, from_year, to_year)

@router.get("/companies/{ticker}/cashflow")
def get_cashflow(ticker: str, from_year: Optional[str] = None, to_year: Optional[str] = None):
    """Returns Cash Flow history array."""
    return fetch_history("cashflow", ticker, from_year, to_year)

@router.get("/companies/{ticker}/ratios")
def get_ratios(ticker: str, year: Optional[int] = None):
    """Returns all computed KPIs per year for the company."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM financial_ratios WHERE company_id = ?"
        params = [ticker]
        
        if year:
            query += " AND year = ?"
            params.append(year)
            
        query += " ORDER BY year ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@router.get("/companies/{ticker}/tearsheet")
def get_tearsheet_pdf(ticker: str):
    """Returns the pre-generated tearsheet PDF as a binary file download."""
    pdf_path = TEARSHEETS_DIR / f"{ticker}_Tearsheet.pdf"
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Tearsheet not found for {ticker}")
        
    return FileResponse(
        path=pdf_path, 
        media_type="application/pdf", 
        filename=f"{ticker}_Tearsheet.pdf"
    )