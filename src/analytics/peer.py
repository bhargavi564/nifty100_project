import os
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
EXCEL_PATH = BASE_DIR / "data" / "peer_groups.xlsx"


def compute_peer_percentiles(db_path=DB_PATH, excel_path=EXCEL_PATH):
    print("[INFO] Starting Peer Percentile Rankings Calculation...")

    # 1. Load Peer Groups mapping with comprehensive error handling
    if not os.path.exists(excel_path):
        print(f"[CRITICAL] Missing peer groups file at: {excel_path}")
        return "Missing Peer Groups Configuration"

    try:
        # We explicitly force the 'openpyxl' engine to parse the newer Excel formats
        peer_df = pd.read_excel(excel_path, engine="openpyxl")
        print(f"[INFO] Loaded peer mappings for {len(peer_df)} companies.")
        
    except ValueError as ve:
        print("\n" + "!" * 60)
        print("[ERROR] Excel parsing engine error detected!")
        print(f"Details: {ve}")
        print("Reason: The file might be completely empty or formatted incorrectly.")
        print("!" * 60 + "\n")
        return "Excel engine parse failure"
        
    except Exception as e:
        print("\n" + "!" * 60)
        print("[ERROR] Failed to load or read the peer_groups.xlsx file.")
        print(f"Details: {e}")
        print("!" * 60 + "\n")
        return "Excel load failure"

    # 2. Extract raw metrics from SQLite
    if not os.path.exists(db_path):
        print(f"[CRITICAL] Database not found at: {db_path}")
        return "Missing SQLite Database"

    conn = sqlite3.connect(db_path)
    query = "SELECT company_id, metric, value, year FROM company_metrics"
    
    try:
        metrics_df = pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"[ERROR] Could not read from database: {e}")
        conn.close()
        return "Database extraction failed"

    # 3. Merge and compute rankings safely
    merged_df = pd.merge(metrics_df, peer_df, on="company_id", how="left")

    # Handle unassigned peer groups
    unassigned_mask = merged_df["peer_group_name"].isna()
    if unassigned_mask.any():
        unassigned_companies = merged_df.loc[unassigned_mask, "company_id"].unique()
        print(f"[WARNING] No peer group assigned for: {list(unassigned_companies)}")
        merged_df = merged_df.dropna(subset=["peer_group_name"])

    # Filter target metrics
    target_metrics = [
        "ROE", "ROCE", "Net Profit Margin", "D/E", "FCF", 
        "PAT CAGR 5yr", "Revenue CAGR 5yr", "EPS CAGR 5yr", 
        "Interest Coverage", "Asset Turnover"
    ]
    merged_df = merged_df[merged_df["metric"].isin(target_metrics)].copy()
    merged_df["value"] = pd.to_numeric(merged_df["value"], errors="coerce")
    merged_df = merged_df.dropna(subset=["value"])

    # Compute rankings
    grouped = merged_df.groupby(["peer_group_name", "year", "metric"])
    merged_df["percentile_rank"] = grouped["value"].rank(pct=True)

    # Invert D/E rankings
    de_mask = merged_df["metric"] == "D/E"
    merged_df.loc[de_mask, "percentile_rank"] = 1.0 - merged_df.loc[de_mask, "percentile_rank"]

    # Write back to DB
    final_cols = ["company_id", "peer_group_name", "metric", "value", "percentile_rank", "year"]
    final_df = merged_df[final_cols].copy()

    print("[INFO] Writing results to SQLite 'peer_percentiles' table...")
    final_df.to_sql("peer_percentiles", conn, if_exists="replace", index=False)
    conn.close()

    print("[SUCCESS] Peer Percentile calculations loaded to Database successfully.")
    return "Calculations completed successfully"


if __name__ == "__main__":
    status = compute_peer_percentiles()
    print(f"Execution Status: {status}")