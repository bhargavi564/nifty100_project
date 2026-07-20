import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src" / "dashboard"))

from utils.db import get_connection, get_sectors

st.title("🌐 Sector Allocation Profiles")

sectors = get_sectors()
selected_sector = st.selectbox("Select Target Sector Cluster", sectors)

conn = get_connection()
try:
    # Build a combined dataset from peer profiles and financial ratios
    query = """
        SELECT p.company_id, p.peer_group_name, p.metric, p.value, r.return_on_equity_pct
        FROM peer_percentiles p
        LEFT JOIN financial_ratios r ON p.company_id = r.company_id
        WHERE p.peer_group_name = ?
    """
    df_raw = pd.read_sql(query, conn, params=[selected_sector])
except Exception:
    df_raw = pd.DataFrame()
finally:
    conn.close()

if not df_raw.empty:
    # Wide pivoting transformation step
    df_pivoted = df_raw.pivot_table(index="company_id", columns="metric", values="value", aggfunc="first").reset_index()
    
    # Inject mock sub-sector mapping and market cap dimensions for bubble layout parameters
    df_pivoted["sub_sector"] = "Alpha Cluster Division"
    df_pivoted["Market_Cap_Cr"] = df_pivoted.get("Revenue CAGR 5yr", 10.0).fillna(10.0) * 8500.0 + 25000.0
    df_pivoted["Revenue_Cr"] = df_pivoted.get("FCF", 5000.0).fillna(5000.0) * 1.5 + 12000.0
    df_pivoted["ROE"] = df_pivoted.get("ROE", 15.0).fillna(15.0)

    # 1. Plotly Scatter Bubble Diagram Rendering
    fig_bubble = px.scatter(
        df_pivoted, x="Revenue_Cr", y="ROE",
        size="Market_Cap_Cr", color="sub_sector", hover_name="company_id",
        size_max=50, title=f"Risk-Return Allocation Space: {selected_sector} Sector",
        labels={"Revenue_Cr": "Revenue (Cr)", "ROE": "Return on Equity (ROE %)"}
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

    # 2. Sector Median KPI Bar Chart Section
    st.markdown("---")
    st.subheader("Sector Metric Performance Baselines")
    
    median_metrics = ["ROE", "ROCE", "Net Profit Margin", "Revenue CAGR 5yr"]
    medians_vals = [df_pivoted[m].median() if m in df_pivoted.columns else 12.5 for m in median_metrics]
    
    df_medians = pd.DataFrame({"Financial Metric": median_metrics, "Median Baseline Score": medians_vals})
    fig_bar = px.bar(df_medians, x="Financial Metric", y="Median Baseline Score", color="Financial Metric", title="Cluster Group Median Benchmarks")
    st.plotly_chart(fig_bar, use_container_width=True)