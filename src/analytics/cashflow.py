import os
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
OUTPUT_XLSX = BASE_DIR / "output" / "cashflow_intelligence.xlsx"
OUTPUT_CSV = BASE_DIR / "output" / "distress_alerts.csv"


def free_cash_flow(cfo, cfi):
    """Calculate Free Cash Flow: CFO + CFI (where CFI is typically negative)."""
    return cfo + cfi


def capex_intensity(cfi, sales):
    """Calculate CapEx Intensity: abs(CFI) / Sales * 100."""
    if not sales or sales == 0:
        return 0.0
    return (abs(cfi) / sales) * 100.0


def sign(value):
    """Return '+' for positive, '-' for negative/zero."""
    return "+" if value > 0 else "-"


def capital_pattern(cfo, cfi, cff):
    """Return cash flow sign pattern label (e.g., '+/-/-')."""
    return f"{sign(cfo)}/{sign(cfi)}/{sign(cff)}"


def run_cashflow_intelligence_pipeline(db_path=DB_PATH):
    print("[INFO] Starting Day 31 Cash Flow Intelligence Analytics Pipeline...")

    if not os.path.exists(db_path):
        print(f"[CRITICAL] Database missing at: {db_path}")
        return "Database missing"

    conn = sqlite3.connect(str(db_path))
    try:
        df_cf = pd.read_sql("SELECT * FROM cashflow", conn)
        df_pl = pd.read_sql("SELECT * FROM profitandloss", conn)
        df_bs = pd.read_sql("SELECT * FROM balancesheet", conn)
        df_peers = pd.read_sql("SELECT DISTINCT company_id, peer_group_name FROM peer_percentiles", conn)
    except Exception as e:
        print(f"[ERROR] Database query failed: {e}")
        return "Database query failed"
    finally:
        conn.close()

    if df_cf.empty or df_pl.empty:
        print("[WARNING] Cashflow or Profit & Loss tables are empty.")
        return "No data found"

    # Merge Statements
    df_merged = pd.merge(df_cf, df_pl, on=["company_id", "year"], how="inner", suffixes=("_cf", "_pl"))
    if not df_bs.empty:
        df_merged = pd.merge(df_merged, df_bs[["company_id", "year", "borrowings"]], on=["company_id", "year"], how="left")
    else:
        df_merged["borrowings"] = 0.0

    df_merged = df_merged.sort_values(["company_id", "year"]).copy()

    companies = df_merged["company_id"].unique()
    results = []
    distress_alerts = []

    for comp in companies:
        c_df = df_merged[df_merged["company_id"] == comp].copy()
        if c_df.empty:
            continue

        latest = c_df.iloc[-1]
        prev = c_df.iloc[-2] if len(c_df) >= 2 else latest

        # Numeric Extraction
        cfo_latest = float(latest.get("operating_activity", 0.0) or 0.0)
        cfi_latest = float(latest.get("investing_activity", 0.0) or 0.0)
        cff_latest = float(latest.get("financing_activity", 0.0) or 0.0)
        sales_latest = float(latest.get("sales", 1.0) or 1.0)
        pat_latest = float(latest.get("net_profit", 1.0) or 1.0)
        borrowings_latest = float(latest.get("borrowings", 0.0) or 0.0)
        borrowings_prev = float(prev.get("borrowings", 0.0) or 0.0)

        # 1. CFO Quality Score (5-Year Avg CFO/PAT)
        c_df["cfo_pat_ratio"] = c_df["operating_activity"] / c_df["net_profit"].replace(0, np.nan)
        cfo_quality_score = c_df["cfo_pat_ratio"].tail(5).mean()
        if pd.isna(cfo_quality_score):
            cfo_quality_score = 1.0

        if cfo_quality_score > 1.0:
            cfo_quality_label = "High Quality"
        elif 0.5 <= cfo_quality_score <= 1.0:
            cfo_quality_label = "Moderate"
        else:
            cfo_quality_label = "Accrual Risk"

        # 2. CapEx Intensity (% of Sales)
        capex_pct = capex_intensity(cfi_latest, sales_latest)
        if capex_pct < 3.0:
            capex_label = "Asset Light"
        elif 3.0 <= capex_pct <= 8.0:
            capex_label = "Moderate"
        else:
            capex_label = "Capital Intensive"

        # 3. FCF Calculations
        fcf_latest = free_cash_flow(cfo_latest, cfi_latest)
        fcf_conversion_pct = (fcf_latest / pat_latest * 100) if pat_latest != 0 else 0.0

        # Compute 5-Year FCF CAGR if history exists
        if len(c_df) >= 5:
            fcf_start = free_cash_flow(c_df.iloc[0]["operating_activity"], c_df.iloc[0]["investing_activity"])
            if fcf_start > 0 and fcf_latest > 0:
                fcf_cagr_5yr = ((fcf_latest / fcf_start) ** (1 / 5) - 1) * 100
            else:
                fcf_cagr_5yr = 0.0
        else:
            fcf_cagr_5yr = 0.0

        # 4. Distress Signal Detection
        distress_flag = (cfo_latest < 0) and (cff_latest > 0)

        # 5. Deleveraging Flag
        deleveraging_flag = (cff_latest < 0) and (borrowings_latest < borrowings_prev)

        # Capital Allocation Label
        cap_alloc_label = capital_pattern(cfo_latest, cfi_latest, cff_latest)

        sector_name = df_peers[df_peers["company_id"] == comp]["peer_group_name"].values
        sector = sector_name[0] if len(sector_name) > 0 else "General"

        results.append({
            "company_id": comp,
            "sector": sector,
            "cfo_quality_score": round(cfo_quality_score, 4),
            "cfo_quality_label": cfo_quality_label,
            "capex_intensity_pct": round(capex_pct, 2),
            "capex_label": capex_label,
            "fcf_cagr_5yr": round(fcf_cagr_5yr, 2),
            "fcf_conversion_pct": round(fcf_conversion_pct, 2),
            "distress_flag": distress_flag,
            "deleveraging_flag": deleveraging_flag,
            "capital_allocation_label": cap_alloc_label
        })

        if distress_flag:
            distress_alerts.append({
                "company_id": comp,
                "cfo_value": cfo_latest,
                "cff_value": cff_latest,
                "latest_net_profit": pat_latest
            })

    # Save Outputs
    df_out = pd.DataFrame(results)
    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_excel(OUTPUT_XLSX, index=False)
    print(f"[SUCCESS] Exported summary to: {OUTPUT_XLSX}")

    df_alerts = pd.DataFrame(distress_alerts)
    df_alerts.to_csv(OUTPUT_CSV, index=False)
    print(f"[SUCCESS] Exported {len(df_alerts)} distress alert entries to: {OUTPUT_CSV}")

    return "Success"


if __name__ == "__main__":
    run_cashflow_intelligence_pipeline()