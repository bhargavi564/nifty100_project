import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "reports" / "radar_charts"


def generate_radar_charts(db_path=DB_PATH, output_dir=OUTPUT_DIR):
    print("[INFO] Starting Day 19 Radar Chart Generation...")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    if not os.path.exists(db_path):
        print(f"[CRITICAL] Database file missing at: {db_path}")
        return "Database missing"

    conn = sqlite3.connect(db_path)
    
    # Query peer percentiles data
    query = """
        SELECT company_id, peer_group_name, metric, percentile_rank, year 
        FROM peer_percentiles
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"[ERROR] Could not query database: {e}")
        conn.close()
        return "Database query failed"
    finally:
        conn.close()

    if df.empty:
        print("[WARNING] No percentile records found in database.")
        return "No data found"

    # Define our 8 target axes
    axes_metrics = [
        "ROE", "ROCE", "Net Profit Margin", "D/E", 
        "FCF", "PAT CAGR 5yr", "Revenue CAGR 5yr", "Composite Score"
    ]
    
    # Standardize metric names to match our DB spelling
    # If "Composite Score" is named "composite_quality_score" in your DB, we rename it on the fly
    df["metric"] = df["metric"].replace({"composite_quality_score": "Composite Score"})
    df_filtered = df[df["metric"].isin(axes_metrics)].copy()

    # Calculate global (Nifty 100) average for unassigned companies
    global_avg = df_filtered.groupby("metric")["percentile_rank"].mean().to_dict()

    # Get unique list of companies
    companies = df_filtered["company_id"].unique()
    num_metrics = len(axes_metrics)
    
    # Calculate angular divisions on the circle (polar coordinates)
    angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    angles += angles[:1]  # Close the loop

    print(f"[INFO] Generating charts for {len(companies)} companies...")

    for company in companies:
        company_data = df_filtered[df_filtered["company_id"] == company]
        peer_group = company_data["peer_group_name"].iloc[0] if not company_data["peer_group_name"].isna().all() else None
        
        # 1. Gather Company Percentiles (mapping them to our 8 predefined axes)
        comp_scores = []
        for metric in axes_metrics:
            val = company_data[company_data["metric"] == metric]["percentile_rank"].values
            comp_scores.append(val[0] if len(val) > 0 else 0.0)
        comp_scores += comp_scores[:1]  # Close the loop
        
        # 2. Gather Peer Group (or Nifty 100) Averages
        peer_scores = []
        if peer_group and peer_group != "No peer group assigned":
            peer_df = df_filtered[df_filtered["peer_group_name"] == peer_group]
            for metric in axes_metrics:
                val = peer_df[peer_df["metric"] == metric]["percentile_rank"].mean()
                peer_scores.append(val if not pd.isna(val) else 0.0)
        else:
            # Fallback to Nifty 100 averages
            for metric in axes_metrics:
                peer_scores.append(global_avg.get(metric, 0.5))
        peer_scores += peer_scores[:1]  # Close the loop

        # 3. Plotting Polar / Radar Chart
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        # Draw the axes lines and labels
        plt.xticks(angles[:-1], axes_metrics, color="grey", size=9)
        ax.set_rlabel_position(30)
        plt.yticks([0.25, 0.50, 0.75, 1.00], ["25th", "50th", "75th", "100th"], color="grey", size=7)
        plt.ylim(0, 1)

        # Plot Company values (Filled Polygon)
        ax.plot(angles, comp_scores, linewidth=1.5, linestyle="solid", label=company, color="#1f77b4")
        ax.fill(angles, comp_scores, color="#1f77b4", alpha=0.35)

        # Plot Peer / Nifty average (Dashed Line Overlay)
        avg_label = f"{peer_group} Avg" if peer_group else "Nifty 100 Avg"
        ax.plot(angles, peer_scores, linewidth=1.5, linestyle="dashed", label=avg_label, color="#ff7f0e")

        # Visual layout adjustments
        plt.title(f"Performance Profile - {company}", size=12, color="#333333", y=1.1, weight="bold")
        plt.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1), fontsize=8)
        
        # Save as PNG
        file_name = output_dir / f"{company}_radar.png"
        plt.savefig(file_name, bbox_inches="tight", dpi=150)
        plt.close()

    print(f"[SUCCESS] Exported {len(companies)} radar charts to: {output_dir}")
    return "Generation complete"


if __name__ == "__main__":
    generate_radar_charts()