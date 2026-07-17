import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

# Resolve path mappings
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src" / "dashboard"))

from utils.db import get_connection, get_sectors

st.title("⚖️ Industry Peer Comparisons")

# 1. Peer Group Dropdown Menu
sectors = get_sectors()
selected_sector = st.selectbox("Select Peer Group Sector", sectors if sectors else ["IT Services", "Banking", "FMCG"])

conn = get_connection()
try:
    query = "SELECT * FROM peer_percentiles WHERE peer_group_name = ?"
    df_peers = pd.read_sql(query, conn, params=[selected_sector])
except Exception:
    df_peers = pd.DataFrame()
finally:
    conn.close()

if not df_peers.empty:
    # 2. Side-by-Side Metric Grid Table Processing
    st.subheader(f"Performance Matrix: {selected_sector} Sector Universe")
    
    pivoted_vals = df_peers.pivot_table(
        index="company_id", columns="metric", values="value", aggfunc="first"
    ).reset_index()
    
    # Highlight the primary benchmark company row (sample assignment: first company)
    benchmark_company = pivoted_vals["company_id"].iloc[0]
    
    def highlight_benchmark(row):
        return ['background-color: #FFD700' if row["company_id"] == benchmark_company else '' for _ in row]
    
    st.dataframe(pivoted_vals.style.apply(highlight_benchmark, axis=1), use_container_width=True)
    st.caption(f"💡 Row highlighted in Gold denotes the active industry group benchmark company: **{benchmark_company}**.")

    # 3. Radar Chart Processing with Plotly Scatterpolar
    st.markdown("---")
    st.subheader("Relative Visual Fingerprint (Percentile Radar Analysis)")
    
    selected_company = st.selectbox("Select Target Company for Radar Profile", pivoted_vals["company_id"].unique())
    
    radar_metrics = ["ROE", "ROCE", "Net Profit Margin", "D/E", "FCF", "PAT CAGR 5yr", "Revenue CAGR 5yr", "Composite Score"]
    
    # Extract company percentiles mapping
    comp_df = df_peers[(df_peers["company_id"] == selected_company) & (df_peers["metric"].isin(radar_metrics))]
    comp_ratios = []
    group_ratios = []
    
    for metric in radar_metrics:
        c_val = comp_df[comp_df["metric"] == metric]["percentile_rank"].values
        comp_ratios.append(c_val[0] if len(c_val) > 0 else 0.5)
        
        g_val = df_peers[df_peers["metric"] == metric]["percentile_rank"].mean()
        group_ratios.append(g_val if pd.notna(g_val) else 0.5)
        
    # Close loops for polar connection path drawing
    comp_ratios += comp_ratios[:1]
    group_ratios += group_ratios[:1]
    radar_metrics_closed = radar_metrics + [radar_metrics[0]]

    # Construct the Plotly radar chart figure
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=comp_ratios, theta=radar_metrics_closed, fill='toself', name=selected_company, line_color="#1f77b4"
    ))
    fig.add_trace(go.Scatterpolar(
        r=group_ratios, theta=radar_metrics_closed, mode='lines', name=f"{selected_sector} Group Avg", line=dict(dash='dash', color="#ff7f0e")
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title=f"Relative Percentile Signature: {selected_company} vs Industry Average"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No peer-relative records are configured in your SQLite tables for this group selector option.")