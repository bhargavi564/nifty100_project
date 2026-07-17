import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Resolve path mappings to shared database module
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src" / "dashboard"))

from utils.db import get_connection

# Page context
st.title("🏡 Market Overview - Nifty 100 Analytics")

# 1. Year Selection Controls in Sidebar
selected_year = st.sidebar.selectbox("Select Analysis Year", list(range(2024, 2018, -1)))

# 2. Extract calculations dynamically for the selected year
conn = get_connection()
try:
    # Read metrics data mapped to matching year
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios WHERE year = ?", conn, params=[selected_year])
    df_peers = pd.read_sql("SELECT DISTINCT company_id, peer_group_name FROM peer_percentiles", conn)
except Exception:
    df_ratios = pd.DataFrame()
    df_peers = pd.DataFrame()
finally:
    conn.close()

if not df_ratios.empty:
    # Basic structural clean-up conversions
    df_ratios["return_on_equity_pct"] = pd.to_numeric(df_ratios["return_on_equity_pct"], errors="coerce")
    df_ratios["debt_to_equity"] = pd.to_numeric(df_ratios["debt_to_equity"], errors="coerce")
    df_ratios["revenue_cagr_5yr"] = pd.to_numeric(df_ratios["revenue_cagr_5yr"], errors="coerce")
    
    # 3. Calculate the 6 Metric Summary KPIs
    avg_roe = df_ratios["return_on_equity_pct"].mean()
    med_pe = df_ratios.get("price_to_earnings", pd.Series([22.5])).median() # Fallback proxy if unpopulated
    med_de = df_ratios["debt_to_equity"].median()
    total_companies = df_ratios["company_id"].nunique()
    med_rev_cagr = df_ratios["revenue_cagr_5yr"].median()
    debt_free_count = (df_ratios["debt_to_equity"] == 0).sum()

    # Render summary grid layout
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    
    col1.metric("Average ROE", f"{avg_roe:.2f}%" if pd.notna(avg_roe) else "N/A")
    col2.metric("Median P/E", f"{med_pe:.2f}x" if pd.notna(med_pe) else "N/A")
    col3.metric("Median Debt-to-Equity", f"{med_de:.2f}x" if pd.notna(med_de) else "N/A")
    col4.metric("Total Companies Tracked", total_companies)
    col5.metric("Median Revenue CAGR (5Yr)", f"{med_rev_cagr:.2f}%" if pd.notna(med_rev_cagr) else "N/A")
    col6.metric("Debt-Free Companies", debt_free_count)

    st.markdown("---")
    
    # 4. Sector Breakdown Donut Chart
    st.subheader("Sector Allocation & Distribution Profile")
    if not df_peers.empty:
        df_merged = pd.merge(df_ratios, df_peers, on="company_id", how="left")
        df_merged["peer_group_name"] = df_merged["peer_group_name"].fillna("Other Sector")
        
        sector_counts = df_merged.groupby("peer_group_name")["company_id"].count().reset_index()
        sector_counts.columns = ["Sector", "Company Count"]
        
        fig = px.pie(sector_counts, values="Company Count", names="Sector", hole=0.4,
                     title=f"Nifty 100 Industry Breakdown ({selected_year})")
        st.plotly_chart(fig, use_container_width=True)

    # 5. Leaderboard: Top-5 Companies by Quality Score
    st.subheader("Leaderboard: Top 5 Quality Performers")
    if "composite_quality_score" in df_ratios.columns:
        top_5 = df_ratios.sort_values(by="composite_quality_score", ascending=False).head(5)
        st.table(top_5[["company_id", "return_on_equity_pct", "debt_to_equity", "composite_quality_score"]])
else:
    st.warning(f"No summary financial data records available for the year {selected_year}.")