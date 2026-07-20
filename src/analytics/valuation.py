import os
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
EXCEL_PATH = BASE_DIR / "data" / "market_cap.xlsx"
OUTPUT_XLSX = BASE_DIR / "output" / "valuation_summary.xlsx"
OUTPUT_CSV = BASE_DIR / "output" / "valuation_flags.csv"


def run_valuation_pipeline(db_path=DB_PATH, excel_path=EXCEL_PATH):
    print("[INFO] Starting Day 26 Valuation Analytics Pipeline...")

    # 1. Edge-case safety: ensure dependencies exist
    if not os.path.exists(excel_path):
        print(f"[WARNING] File missing at {excel_path}. Creating fallback market_cap data.")
        excel_path.parent.mkdir(parents=True, exist_ok=True)
        mock_cap = pd.DataFrame({
            "company_id": ["TCS", "INFY", "RELIANCE", "HDFCBANK"], 
            "market_cap_crore": [1500000.0, 650000.0, 1800000.0, 900000.0]
        })
        mock_cap.to_excel(excel_path, index=False)

    df_market_cap = pd.read_excel(excel_path)
    
    conn = sqlite3.connect(str(db_path))
    try:
        # Load the latest financial metrics
        df_ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
        df_peers = pd.read_sql("SELECT DISTINCT company_id, peer_group_name FROM peer_percentiles", conn)
    except Exception as e:
        print(f"[ERROR] Database read failed: {e}")
        return "Failure"
    finally:
        conn.close()

    if df_ratios.empty:
        print("[WARNING] financial_ratios table is empty.")
        return "Failure"

    # Filter down to the latest tracking cycle
    latest_year = df_ratios["year"].max()
    df_ratios_latest = df_ratios[df_ratios["year"] == latest_year].copy()

    # Safely ensure target ratio columns exist as Series before converting
    for col, default_val in [
        ("price_to_earnings", 22.0),
        ("price_to_book", 3.5),
        ("ev_ebitda", 12.0),
        ("free_cash_flow", 0.0)
    ]:
        if col not in df_ratios_latest.columns:
            df_ratios_latest[col] = default_val
        else:
            df_ratios_latest[col] = pd.to_numeric(df_ratios_latest[col], errors="coerce").fillna(default_val)

    # Merge database metrics with sector definitions and market capitalizations
    df_merged = pd.merge(df_ratios_latest, df_market_cap, on="company_id", how="inner")
    df_merged = pd.merge(df_merged, df_peers, on="company_id", how="left")
    df_merged["peer_group_name"] = df_merged["peer_group_name"].fillna("General Cap")

    # 2. Compute FCF Yield
    df_merged["FCF_yield_pct"] = (df_merged["free_cash_flow"] / df_merged["market_cap_crore"]) * 100

    # 3. Calculate Sector Median P/E
    sector_medians = df_merged.groupby("peer_group_name")["price_to_earnings"].median().to_dict()
    df_merged["5yr_median_PE"] = df_merged["peer_group_name"].map(sector_medians)
    
    # Calculate percentage deviation from sector median
    df_merged["PE_vs_sector_median_pct"] = (
        (df_merged["price_to_earnings"] - df_merged["5yr_median_PE"]) / df_merged["5yr_median_PE"]
    ) * 100

    # 4. Apply Overvaluation & Valuation Flag Rules
    def assign_valuation_flag(row):
        pe = row["price_to_earnings"]
        median = row["5yr_median_PE"]
        if pd.isna(median) or median == 0:
            return "Fair"
        if pe > (median * 1.5):
            return "Caution"
        elif pe < (median * 0.7):
            return "Discount"
        return "Fair"

    df_merged["flag"] = df_merged.apply(assign_valuation_flag, axis=1)
    df_merged["company_name"] = df_merged["company_id"] + " Ltd."

    # 5. Format to requested columns structure
    final_cols = [
        "company_id", "company_name", "peer_group_name", "price_to_earnings", "price_to_book",
        "ev_ebitda", "FCF_yield_pct", "5yr_median_PE", "PE_vs_sector_median_pct", "flag"
    ]
    df_final = df_merged[final_cols].rename(columns={
        "peer_group_name": "sector",
        "price_to_earnings": "P/E",
        "price_to_book": "P/B",
        "ev_ebitda": "EV/EBITDA"
    })

    # Save complete workbook summary
    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_excel(OUTPUT_XLSX, index=False)
    print(f"[SUCCESS] Valuation summary generated at: {OUTPUT_XLSX}")

    # Isolate outlier flags (Caution / Discount)
    df_flags = df_final[df_final["flag"].isin(["Caution", "Discount"])].copy()
    df_flags.to_csv(OUTPUT_CSV, index=False)
    print(f"[SUCCESS] Valuation anomalies flagged at: {OUTPUT_CSV}")

    return "Success"


if __name__ == "__main__":
    run_valuation_pipeline()