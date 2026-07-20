import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src" / "dashboard"))

from utils.db import get_connection, get_companies

st.title("📈 Historical Trend Analytics")

company_list = get_companies()
selected_company = st.selectbox("Select Target Company", company_list)

# Metric multi-selector configuration (cap selections at 3 max)
metric_choices = ["return_on_equity_pct", "operating_profit_margin_pct", "net_profit_margin_pct", "debt_to_equity", "asset_turnover"]
selected_metrics = st.multiselect("Select Overlay Metrics (Max 3)", metric_choices, default=["return_on_equity_pct"])

if len(selected_metrics) > 3:
    st.error("⚠️ Selection overflow: Please remove metrics to stick to the 3-metric comparison cap limit.")
elif selected_company and len(selected_metrics) > 0:
    conn = get_connection()
    try:
        query = f"SELECT year, {', '.join(selected_metrics)} FROM financial_ratios WHERE company_id = ? ORDER BY year ASC"
        df_trends = pd.read_sql(query, conn, params=[selected_company])
    except Exception:
        df_trends = pd.DataFrame()
    finally:
        conn.close()

    if not df_trends.empty and len(df_trends) > 1:
        fig = go.Figure()

        for col in selected_metrics:
            df_trends[col] = pd.to_numeric(df_trends[col], errors="coerce")
            
            # Calculate YoY % changes explicitly for text annotation injection
            yoy_changes = [""]
            for i in range(1, len(df_trends)):
                prev = df_trends[col].iloc[i-1]
                curr = df_trends[col].iloc[i]
                if prev and prev != 0 and pd.notna(prev) and pd.notna(curr):
                    change = ((curr - prev) / abs(prev)) * 100
                    yoy_changes.append(f"{change:+.1f}% YoY")
                else:
                    yoy_changes.append("0.0%")

            fig.add_trace(go.Scatter(
                x=df_trends["year"], y=df_trends[col],
                mode="lines+markers+text",
                name=col.replace("_", " ").title(),
                text=yoy_changes,
                textposition="top center",
                textfont=dict(size=8)
            ))

        fig.update_layout(title=f"10-Year Dynamic Trend Overlay: {selected_company}", xaxis_title="Fiscal Year", yaxis_title="Metric Value Scale")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Insufficient multi-year records to map trend progressions.")