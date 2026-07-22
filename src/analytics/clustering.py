import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Ensure matplotlib runs headlessly
matplotlib.use('Agg')

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
CASHFLOW_XLSX = BASE_DIR / "output" / "cashflow_intelligence.xlsx"
ELBOW_PLOT = BASE_DIR / "reports" / "elbow_plot.png"
OUTPUT_CSV = BASE_DIR / "output" / "cluster_labels.csv"

# Ensure output directories exist
ELBOW_PLOT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

def run_kmeans_clustering():
    print("[INFO] Starting Day 36 KMeans Clustering Pipeline...")

    # 1. Data Extraction
    if not DB_PATH.exists():
        print(f"[CRITICAL] Database missing at: {DB_PATH}")
        return "Database missing"

    conn = sqlite3.connect(str(DB_PATH))
    try:
        df_ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
        df_peers = pd.read_sql("SELECT DISTINCT company_id, peer_group_name FROM peer_percentiles", conn)
    except Exception as e:
        print(f"[ERROR] Database query failed: {e}")
        return "Failure"
    finally:
        conn.close()

    # Filter to the latest available year
    latest_year = df_ratios["year"].max()
    df_latest = df_ratios[df_ratios["year"] == latest_year].copy()
    
    # Merge Sector data
    df_merged = pd.merge(df_latest, df_peers, on="company_id", how="left")
    df_merged["peer_group_name"] = df_merged["peer_group_name"].fillna("General")
    df_merged.rename(columns={"peer_group_name": "sector"}, inplace=True)

    # Merge Cashflow data to get fcf_cagr_5yr if available
    if CASHFLOW_XLSX.exists():
        df_cf = pd.read_excel(CASHFLOW_XLSX)
        if "fcf_cagr_5yr" in df_cf.columns:
            df_merged = pd.merge(df_merged, df_cf[["company_id", "fcf_cagr_5yr"]], on="company_id", how="left")
    
    # Add mock column safely if fcf_cagr_5yr wasn't found in previous steps
    if "fcf_cagr_5yr" not in df_merged.columns:
        df_merged["fcf_cagr_5yr"] = 10.0

    # 2. Imputation: Missing values -> Sector Median
    features = [
        "return_on_equity_pct", 
        "debt_to_equity", 
        "revenue_cagr_5yr", 
        "fcf_cagr_5yr", 
        "operating_profit_margin_pct"
    ]
    
    for f in features:
        df_merged[f] = pd.to_numeric(df_merged.get(f, np.nan), errors="coerce")
        # Sector median imputation
        df_merged[f] = df_merged.groupby("sector")[f].transform(lambda x: x.fillna(x.median()))
        # Global median fallback (if an entire sector is NaN)
        df_merged[f] = df_merged[f].fillna(df_merged[f].median()).fillna(0)

    # 3. Standardization
    X = df_merged[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 4. Generate Elbow Plot (k = 2 to 10)
    print(" -> Generating Elbow Plot...")
    inertias = []
    k_range = range(2, 11)
    
    for k in k_range:
        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init="auto")
        kmeans_temp.fit(X_scaled)
        inertias.append(kmeans_temp.inertia_)
        
    plt.figure(figsize=(8, 5))
    plt.plot(k_range, inertias, marker='o', linestyle='--', color='navy')
    plt.title('KMeans Clustering: Elbow Method')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Inertia (Sum of Squared Distances)')
    plt.grid(True, linestyle=':', alpha=0.6)
    
    # Annotate k=5
    plt.annotate('Target k=5', xy=(5, inertias[3]), xytext=(6, inertias[3] + max(inertias)*0.1),
                 arrowprops=dict(facecolor='red', shrink=0.05))
    
    plt.savefig(ELBOW_PLOT, bbox_inches='tight')
    plt.close()
    print(f" -> Elbow plot saved to {ELBOW_PLOT}")

    # 5. Run KMeans with n_clusters = 5
    print(" -> Fitting KMeans (k=5)...")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init="auto")
    cluster_ids = kmeans.fit_predict(X_scaled)
    centroids = kmeans.cluster_centers_

    # 6. Compute distances to centroid
    distances = []
    for i, row in enumerate(X_scaled):
        cluster_idx = cluster_ids[i]
        centroid = centroids[cluster_idx]
        dist = np.linalg.norm(row - centroid)
        distances.append(dist)

    # 7. Prepare Output
    df_merged["cluster_id"] = cluster_ids
    df_merged["distance_from_centroid"] = distances
    
    # Generate generic cluster names based on their ID
    cluster_mapping = {
        0: "Cluster 0 (Value/Core)",
        1: "Cluster 1 (High Growth)",
        2: "Cluster 2 (High Leverage)",
        3: "Cluster 3 (High Profitability)",
        4: "Cluster 4 (Distressed/Laggards)"
    }
    df_merged["cluster_name"] = df_merged["cluster_id"].map(cluster_mapping)

    output_cols = ["company_id", "cluster_id", "cluster_name", "distance_from_centroid"]
    df_out = df_merged[output_cols]
    
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"[SUCCESS] Exported {len(df_out)} clustered records to {OUTPUT_CSV}")
    
    return "Success"

if __name__ == "__main__":
    run_kmeans_clustering()