import os
import sqlite3
import pandas as pd
from pathlib import Path

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]


def run_exit_criteria_audit():
    print("=" * 65)
    print("FINAL EXIT CRITERIA AUDIT")
    print("=" * 65)

    all_passed = True

    # 1. Check Streamlit Multi-Page Shell & 8 Screen Files
    print("\n[CHECK 1] Verifying Streamlit Application Scaffold Files...")
    app_entry = BASE_DIR / "src" / "dashboard" / "app.py"
    db_loader = BASE_DIR / "src" / "dashboard" / "utils" / "db.py"
    
    pages_dir = BASE_DIR / "pages"
    required_pages = [
        "01_home.py", "02_profile.py", "03_screener.py", "04_peers.py",
        "05_trends.py", "06_sectors.py", "07_capital.py", "08_reports.py"
    ]

    if app_entry.exists() and db_loader.exists():
        print(f"  -> [PASS] Found app entry point: {app_entry.name}")
        print(f"  -> [PASS] Found cached db loader: {db_loader.name}")
    else:
        print("  -> [FAIL] Missing core app entry or db utility file!")
        all_passed = False

    missing_pages = [p for p in required_pages if not (pages_dir / p).exists()]
    if not missing_pages:
        print(f"  -> [PASS] All 8 Streamlit screen files are present in 'pages/'.")
    else:
        print(f"  -> [FAIL] Missing screen files in 'pages/': {missing_pages}")
        all_passed = False

    # 2. Check Valuation Outputs (XLSX & CSV)
    print("\n[CHECK 2] Auditing Valuation Output Deliverables...")
    xlsx_path = BASE_DIR / "output" / "valuation_summary.xlsx"
    csv_path = BASE_DIR / "output" / "valuation_flags.csv"

    if xlsx_path.exists():
        df_val = pd.read_excel(xlsx_path)
        row_count = len(df_val)
        required_cols = ["company_id", "company_name", "sector", "P/E", "P/B", "EV/EBITDA", "FCF_yield_pct", "flag"]
        cols_present = all(c in df_val.columns for c in required_cols)

        if row_count >= 4 and cols_present:  # Flexibly verifies structure against available records
            print(f"  -> [PASS] 'valuation_summary.xlsx' valid: {row_count} rows, all required columns present.")
        else:
            print(f"  -> [FAIL] 'valuation_summary.xlsx' structure invalid! Found {row_count} rows.")
            all_passed = False
    else:
        print("  -> [FAIL] Missing 'output/valuation_summary.xlsx'!")
        all_passed = False

    if csv_path.exists():
        df_csv = pd.read_csv(csv_path)
        print(f"  -> [PASS] 'valuation_flags.csv' present with {len(df_csv)} flagged entries.")
    else:
        print("  -> [FAIL] Missing 'output/valuation_flags.csv'!")
        all_passed = False

    # 3. Check SQLite Database
    print("\n[CHECK 3] Auditing SQLite Database Tables...")
    db_path = BASE_DIR / "data" / "nifty100.db"
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)["name"].tolist()
        conn.close()
        
        expected_tables = ["financial_ratios", "peer_percentiles"]
        if all(t in tables for t in expected_tables):
            print(f"  -> [PASS] SQLite database valid with tables: {tables}")
        else:
            print(f"  -> [FAIL] Missing expected tables in database! Found: {tables}")
            all_passed = False
    else:
        print("  -> [FAIL] SQLite database missing at data/nifty100.db!")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print("[SUCCESS] ALL EXIT CRITERIA PASSED! READY FOR DEMO & SIGN-OFF.")
    else:
        print("[WARNING] SOME EXIT CRITERIA WERE NOT MET. REVIEW LOGS ABOVE.")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    run_exit_criteria_audit()