import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Resolve path mappings to shared database module
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src" / "dashboard"))

from utils.db import get_connection

st.title("🔍 Fundamental Strategy Screener")

# 1. Define Preset Configurations
presets = {
    "Quality": {"roe_min": 15.0, "de_max": 1.0, "fcf_min": 100.0, "rev_min": 10.0},
    "Value": {"roe_min": 10.0, "de_max": 1.5, "pe_max": 20.0, "pb_max": 3.0, "div_min": 1.5},
    "Growth": {"pat_min": 20.0, "rev_min": 15.0, "de_max": 2.0},
    "Dividend": {"div_min": 2.5, "payout_max": 80.0, "fcf_min": 50.0},
    "Debt-Free": {"de_max": 0.0, "roe_min": 12.0},
    "Turnaround": {"rev_min": 10.0, "fcf_min": 10.0, "de_max": 1.0}
}

# 2. Render Preset Buttons at the top
st.subheader("Strategy Presets Quick-Filter")
cols = st.columns(6)
clicked_preset = None

for idx, name in enumerate(presets.keys()):
    if cols[idx].button(name):
        clicked_preset = name

# 3. Sidebar Sliders Definition with Session State Syncing
st.sidebar.header("Filter Criteria Sliders")

def get_slider_val(key, default_val, is_max=False):
    """Sync slider positions dynamically when preset buttons are pressed."""
    if clicked_preset and key in presets[clicked_preset]:
        return presets[clicked_preset][key]
    return default_val

roe_min = st.sidebar.slider("Minimum ROE (%)", 0.0, 50.0, get_slider_val("roe_min", 0.0))
de_max = st.sidebar.slider("Maximum D/E (x)", 0.0, 5.0, get_slider_val("de_max", 3.0))
fcf_min = st.sidebar.slider("Minimum FCF (Cr)", -500.0, 5000.0, get_slider_val("fcf_min", -500.0))
rev_min = st.sidebar.slider("Minimum 5Yr Revenue CAGR (%)", -10.0, 50.0, get_slider_val("rev_min", -10.0))
pat_min = st.sidebar.slider("Minimum 5Yr PAT CAGR (%)", -10.0, 50.0, get_slider_val("pat_min", -10.0))
opm_min = st.sidebar.slider("Minimum OPM (%)", -5.0, 60.0, get_slider_val("opm_min", -5.0))
pe_max = st.sidebar.slider("Maximum P/E (x)", 5.0, 100.0, get_slider_val("pe_max", 100.0))
pb_max = st.sidebar.slider("Maximum P/B (x)", 0.5, 20.0, get_slider_val("pb_max", 20.0))
div_min = st.sidebar.slider("Minimum Dividend Yield (%)", 0.0, 10.0, get_slider_val("div_min", 0.0))
icr_min = st.sidebar.slider("Minimum Interest Coverage", -5.0, 50.0, get_slider_val("icr_min", -5.0))

# 4. Extract and Filter the Data
conn = get_connection()
try:
    query = """
        SELECT r.company_id, r.year, r.return_on_equity_pct, r.debt_to_equity, r.free_cash_flow,
               r.revenue_cagr_5yr, r.pat_cagr_5yr, r.operating_profit_margin_pct, r.composite_quality_score,
               p.peer_group_name as sector
        FROM financial_ratios r
        LEFT JOIN peer_percentiles p ON r.company_id = p.company_id
    """
    df = pd.read_sql(query, conn)
except Exception:
    df = pd.DataFrame()
finally:
    conn.close()

if not df.empty:
    # Drop duplicates from joining and ensure correct numeric mapping
    df = df.drop_duplicates(subset=["company_id"]).copy()
    df["company_name"] = df["company_id"] + " Ltd."
    
    # Apply conditions sequentially
    mask = (
        (df["return_on_equity_pct"].fillna(0) >= roe_min) &
        (df["debt_to_equity"].fillna(0) <= de_max) &
        (df["free_cash_flow"].fillna(0) >= fcf_min) &
        (df["revenue_cagr_5yr"].fillna(0) >= rev_min) &
        (df["pat_cagr_5yr"].fillna(0) >= pat_min) &
        (df["operating_profit_margin_pct"].fillna(0) >= opm_min)
    )
    
    filtered_df = df[mask].copy()
    
    # 5. Display Count Label and Filtered Results Table
    st.markdown("---")
    st.subheader(f"📊 Results: {len(filtered_df)} companies match your active filters")
    
    display_cols = ["company_id", "company_name", "sector", "composite_quality_score", 
                    "return_on_equity_pct", "debt_to_equity", "free_cash_flow", "revenue_cagr_5yr"]
    
    st.dataframe(filtered_df[display_cols], use_container_width=True)
    
    # 6. CSV Download Button Link
    csv_data = filtered_df[display_cols].to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_data,
        file_name="screener_filtered_output.csv",
        mime="text/csv"
    )
else:
    st.error("No core ratio database assets are active to support the screen execution layout.")