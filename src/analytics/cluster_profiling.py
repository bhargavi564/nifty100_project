import os
import sqlite3
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path

# Ensure matplotlib runs headlessly
matplotlib.use('Agg')

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
CLUSTER_CSV = BASE_DIR / "output" / "cluster_labels.csv"
CASHFLOW_XLSX = BASE_DIR / "output" / "cashflow_intelligence.xlsx"

HEATMAP_PLOT = BASE_DIR / "reports" / "correlation_heatmap.png"
OUTLIER_CSV = BASE_DIR / "output" / "outlier_report.csv"
STATS_CSV = BASE_DIR / "output" / "portfolio_stats.csv"
PROFILE_CSV = BASE_DIR / "output" / "cluster_profiles.csv"

# Ensure output directories exist
HEATMAP_PLOT.parent.mkdir(parents=True, exist_ok=True)
OUTLIER_CSV.parent.mkdir(parents=True, exist_ok=True)


def safe_zscore(x):
    """Calculates Z-score safely, returning 0 if standard deviation is 0."""
    std = x.std(ddof=0)
    if std == 0 or pd.isna(std):
        return np.zeros_like(x)
    return (x - x.mean()) / std


def run_cluster_profiling_and_stats():
    print("[INFO] Starting Day 37 Cluster Profiling & Statistics Pipeline...")

    if not DB_PATH.exists():
        print(f"[CRITICAL] Database missing at: {DB_PATH}")
        return "Database missing"

    # 1. Data Extraction
    conn = sqlite3.connect(str(DB_PATH))
    try:
        df_ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
        df_peers = pd.read_sql("SELECT DISTINCT company_id, peer_group_name FROM peer_percentiles", conn)
    except Exception as e:
        print(f"[ERROR] DB read failed: {e}")
        return "Failure"
    finally:
        conn.close()

    if df_ratios.empty:
        print("[WARNING] financial_ratios table is empty.")
        return "Failure"

    # Filter to latest year
    latest_year = df_ratios["year"].max()
    df_latest = df_ratios[df_ratios["year"] == latest_year].copy()
    
    # Merge Sector data
    df_merged = pd.merge(df_latest, df_peers, on="company_id", how="left")
    df_merged["peer_group_name"] = df_merged["peer_group_name"].fillna("General")
    df_merged.rename(columns={"peer_group_name": "sector"}, inplace=True)

    # 10 KPIs for Correlation & Stats
    kpis = [
        "return_on_equity_pct", "debt_to_equity", "operating_profit_margin_pct", 
        "net_profit_margin_pct", "revenue_cagr_5yr", "pat_cagr_5yr",
        "price_to_earnings", "price_to_book", "ev_ebitda", "interest_coverage"
    ]
    
    # 2. Safely ensure numeric columns exist
    for kpi in kpis:
        if kpi not in df_merged.columns:
            df_merged[kpi] = 0.0
        else:
            df_merged[kpi] = pd.to_numeric(df_merged[kpi], errors="coerce").fillna(0)

    # 3. Cluster Profiling
    cluster_features = ["return_on_equity_pct", "debt_to_equity", "revenue_cagr_5yr", "operating_profit_margin_pct"]
    
    if CLUSTER_CSV.exists():
        df_clusters = pd.read_csv(CLUSTER_CSV)
        df_merged = pd.merge(df_merged, df_clusters[["company_id", "cluster_id"]], on="company_id", how="inner")
        
        # Merge FCF CAGR if available to complete the 5 cluster features
        if CASHFLOW_XLSX.exists():
            df_cf = pd.read_excel(CASHFLOW_XLSX)
            if "fcf_cagr_5yr" in df_cf.columns:
                df_merged = pd.merge(df_merged, df_cf[["company_id", "fcf_cagr_5yr"]], on="company_id", how="left")
        
        if "fcf_cagr_5yr" not in df_merged.columns:
            df_merged["fcf_cagr_5yr"] = 0.0
        
        cluster_features.append("fcf_cagr_5yr")
        
        # Safely enforce numeric cluster columns
        for f in cluster_features:
            if f not in df_merged.columns:
                df_merged[f] = 0.0
            else:
                df_merged[f] = pd.to_numeric(df_merged[f], errors="coerce").fillna(0)

        print("\n--- Cluster Profiles (Mean & Median) ---")
        profiles = df_merged.groupby("cluster_id")[cluster_features].agg(['mean', 'median'])
        profiles.to_csv(PROFILE_CSV)
        print(f" -> Cluster profiles saved to {PROFILE_CSV.name}")
        
        # Descriptive Names mapping based on typical financial clustering logic
        descriptive_names = {
            0: "High-Quality Compounders",
            1: "Defensive Dividend Payers",
            2: "Value Cyclicals",
            3: "Emerging Growth",
            4: "Distressed or Turnaround"
        }
        df_merged["cluster_name"] = df_merged["cluster_id"].map(descriptive_names)

    # 4. Correlation Matrix Heatmap
    print("\n -> Generating Pearson Correlation Heatmap (10 KPIs)...")
    corr_matrix = df_merged[kpis].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0, 
                square=True, linewidths=.5, cbar_kws={"shrink": .75})
    plt.title(f"Pearson Correlation Matrix of 10 Core KPIs ({latest_year})")
    plt.tight_layout()
    plt.savefig(HEATMAP_PLOT)
    plt.close()
    print(f" -> Heatmap saved to {HEATMAP_PLOT.name}")

    # 5. Outlier Detection (Z-Score > 3 per sector)
    print(" -> Running Sector-Level Outlier Detection...")
    outliers = []
    
    for sector, group in df_merged.groupby("sector"):
        for kpi in kpis:
            z_scores = safe_zscore(group[kpi])
            # Find absolute Z-score > 3
            outlier_mask = np.abs(z_scores) > 3
            if outlier_mask.any():
                for idx, is_outlier in outlier_mask.items():
                    if is_outlier:
                        outliers.append({
                            "company_id": group.loc[idx, "company_id"],
                            "sector": sector,
                            "metric": kpi,
                            "value": group.loc[idx, kpi],
                            "z_score": round(z_scores[idx], 2)
                        })
                        
    df_outliers = pd.DataFrame(outliers)
    if not df_outliers.empty:
        df_outliers.to_csv(OUTLIER_CSV, index=False)
        print(f" -> Flagged {len(df_outliers)} statistical outliers across sectors (Saved to {OUTLIER_CSV.name})")
    else:
        # Generate empty dataframe with headers if no outliers
        pd.DataFrame(columns=["company_id", "sector", "metric", "value", "z_score"]).to_csv(OUTLIER_CSV, index=False)
        print(" -> No statistical outliers detected.")

    # 6. Portfolio Statistics Summary
    print(" -> Generating Portfolio Statistics Summary...")
    stats_df = df_merged[kpis].describe(percentiles=[.10, .25, .50, .75, .90]).T
    stats_df = stats_df[['10%', '25%', '50%', '75%', '90%', 'mean', 'std']]
    stats_df.rename(columns={'10%': 'P10', '25%': 'P25', '50%': 'P50', '75%': 'P75', '90%': 'P90', 'mean': 'Mean', 'std': 'Std'}, inplace=True)
    
    stats_df.to_csv(STATS_CSV, index=True, index_label="KPI")
    print(f" -> Portfolio statistics exported to {STATS_CSV.name}")

    return "Success"


if __name__ == "__main__":
    run_cluster_profiling_and_stats()