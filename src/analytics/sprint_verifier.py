import os
import sqlite3
import pandas as pd
from pathlib import Path

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"


def verify_sprint_outputs(db_path=DB_PATH):
    print("=" * 60)
    print("SRE_VERIFIER: RUNNING SPRINT AUTOMATED AUDIT")
    print("=" * 60)

    if not os.path.exists(db_path):
        print(f"[FAIL] Database missing at: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    
    # 1. Verify Peer Percentiles Integrity
    print("\n[CHECK 1] Auditing SQLite 'peer_percentiles' table...")
    try:
        df_percentiles = pd.read_sql_query("SELECT * FROM peer_percentiles", conn)
        total_rows = len(df_percentiles)
        unique_groups = df_percentiles["peer_group_name"].nunique()
        print(f"[PASS] Successfully loaded {total_rows} records across {unique_groups} peer groups.")
    except Exception as e:
        print(f"[FAIL] Peer percentiles table lookup failed: {e}")
        conn.close()
        return False

    # 2. Spot Check: IT Services ROE ranking consistency
    print("\n[CHECK 2] Spot-checking 'IT Services' ROE percentile logic...")
    it_roe = df_percentiles[
        (df_percentiles["peer_group_name"].str.lower() == "it services") & 
        (df_percentiles["metric"] == "ROE")
    ].copy()

    if not it_roe.empty:
        # Sort by raw value descending
        it_roe = it_roe.sort_values(by="value", ascending=False)
        highest_roe_comp = it_roe.iloc[0]["company_id"]
        highest_roe_val = it_roe.iloc[0]["value"]
        highest_roe_rank = it_roe.iloc[0]["percentile_rank"]

        print(f" -> Company with highest ROE in IT: {highest_roe_comp} ({highest_roe_val}%)")
        print(f" -> Assigned ROE Percentile Rank: {highest_roe_rank}")

        if highest_roe_rank == it_roe["percentile_rank"].max():
            print("[PASS] Validation consistent: Highest ROE holds the highest percentile rank.")
        else:
            print("[FAIL] Percentile mismatch: Highest ROE does not hold the top rank.")
    else:
        print("[SKIP] No 'IT Services' ROE records found for spot-check.")

    # 3. Deliverables Audit
    print("\n[CHECK 3] Scanning generated artifacts...")
    required_files = [
        OUTPUT_DIR / "screener_output.xlsx",
        OUTPUT_DIR / "peer_comparison.xlsx",
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if file_path.exists():
            print(f"[PASS] Found: {file_path.name}")
        else:
            print(f"[FAIL] Missing required artifact: {file_path.name}")
            all_files_exist = False

    conn.close()
    print("\n" + "=" * 60)
    print("AUDIT COMPLETED")
    print("=" * 60)
    return all_files_exist


if __name__ == "__main__":
    verify_sprint_outputs()