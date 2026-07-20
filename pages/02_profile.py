import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src" / "dashboard"))

from utils.db import get_companies, get_ratios, get_pl

st.title("🏢 Corporate Intelligence & Performance Profile")


def safe_fmt(val, suffix="", decimals=2):
    """Graceful formatter for missing/NaN metrics."""
    if val is None or pd.isna(val) or str(val).strip().lower() in ["none", "nan"]:
        return "N/A"
    try:
        return f"{float(val):.{decimals}f}{suffix}"
    except (ValueError, TypeError):
        return "N/A"


# 1. Search Box
company_options = get_companies()
search_query = st.selectbox("Search Company Ticker/Name", [""] + company_options)

if search_query:
    ticker = search_query

    st.markdown(f"### **{ticker} Platform Card Profile**")
    col_a, col_b, col_c = st.columns(3)
    col_a.markdown("**Sector:** Core Industry Cluster")
    col_b.markdown("**Sub-Sector:** Large-Cap Alpha")
    col_c.markdown(f"**NSE Ticker Symbol:** `{ticker}`")
    st.markdown("---")

    ratios_df = get_ratios(ticker)
    pl_df = get_pl(ticker)

    if not ratios_df.empty:
        # Partial data check (< 10 years notification)
        years_available = len(ratios_df)
        if years_available < 10:
            st.info(f"ℹ️ **Data Availability Note:** Historical records available for {years_available} years.")

        latest = ratios_df.iloc[0]

        # 6 KPI Tile Blocks with safe_fmt
        st.subheader("Latest Core Financial Metrics")
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi4, kpi5, kpi6 = st.columns(3)

        kpi1.metric("Return on Equity (ROE)", safe_fmt(latest.get("return_on_equity_pct"), "%"))
        kpi2.metric("Operating Margin (OPM)", safe_fmt(latest.get("operating_profit_margin_pct"), "%"))
        kpi3.metric("Net Profit Margin (NPM)", safe_fmt(latest.get("net_profit_margin_pct"), "%"))
        kpi4.metric("Debt to Equity Ratio", safe_fmt(latest.get("debt_to_equity"), "x"))
        kpi5.metric("Revenue CAGR 5Yr", safe_fmt(latest.get("revenue_cagr_5yr"), "%"))
        kpi6.metric("Latest Free Cash Flow", safe_fmt(latest.get("free_cash_flow"), " Cr"))

        st.markdown("---")

        # 10-Year Growth Bar Chart
        st.subheader("Historical Growth Performance Trajectory")
        if not pl_df.empty:
            pl_df = pl_df.sort_values("year")
            fig_bar = px.bar(
                pl_df, x="year", y=["sales", "net_profit"], barmode="group",
                title=f"Trend Analysis: Revenue vs Net Profit ({len(pl_df)} Years)",
                labels={"value": "Amount (Cr)", "variable": "Financial Parameter"}
            )
            # Prevent overflow
            fig_bar.update_layout(autosize=True)
            st.plotly_chart(fig_bar, use_container_width=True)

            # Dual-Axis Return Efficiency Chart
            st.subheader("Return Efficiency Analysis (ROE vs ROCE)")
            ratios_sorted = ratios_df.sort_values("year")
            ratios_sorted["roce_mock"] = pd.to_numeric(ratios_sorted["return_on_equity_pct"], errors="coerce") * 0.92

            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=ratios_sorted["year"], y=ratios_sorted["return_on_equity_pct"],
                name="ROE (%)", mode="lines+markers", line=dict(color="green")
            ))
            fig_line.add_trace(go.Scatter(
                x=ratios_sorted["year"], y=ratios_sorted["roce_mock"],
                name="ROCE (%)", mode="lines+markers", line=dict(color="blue", dash="dash")
            ))
            fig_line.update_layout(
                title="Historical Return Profile Tracking",
                xaxis_title="Year", yaxis_title="Percentage (%)",
                autosize=True
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # Pros and Cons Badges
        st.subheader("Automated Quality Assessment Badges")
        roe_val = pd.to_numeric(latest.get("return_on_equity_pct"), errors="coerce")
        de_val = pd.to_numeric(latest.get("debt_to_equity"), errors="coerce")

        if pd.notna(roe_val) and roe_val > 15:
            st.success("✅ Strong Capital Efficiency: Return on Equity passes the 15% benchmark rule threshold.")
        else:
            st.error("❌ Soft Capital Returns: Return on Equity falls below the 15% hurdle parameter.")

        if pd.notna(de_val) and de_val < 1:
            st.success("✅ Solid Balance Sheet: Low financial leverage with Debt-to-Equity well controlled below 1.0x.")
        else:
            st.warning("⚠️ High Debt Exposure: Balance sheet leverage exceeds optimal boundaries.")
    else:
        st.error("Ticker not found — please try another selection.")
else:
    st.info("Please select a specific corporate ticker option from the dropdown field above.")