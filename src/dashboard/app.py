import streamlit as st
import sys
from pathlib import Path

# Add dashboard and utils directories to path resolving
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "dashboard"))

from utils.db import get_companies

# 1. Page Configuration setting (wide layout, expanded sidebar)
st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Setup structural App Container Shell
st.title("📊 Nifty 100 Corporate Analytics Dashboard")
st.markdown("---")

st.sidebar.title("Navigation Panel")
st.sidebar.success("Select a specific page tab from the list above.")

st.subheader("Welcome to Sprint 3 Analytics Core Suite")
st.info("Navigate to subpages via the sidebar options on your left to explore financial ratios, peer rankings, and trend metrics.")

# 3. Simple verification rendering inside scaffold base shell
st.metric(label="Total Companies Tracked", value=len(get_companies()))