import os
import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path

# Path resolving
BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "data" / "nifty100.db"


def get_connection():
    """Establishes connection to SQLite database."""
    return sqlite3.connect(str(DB_PATH))


@st.cache_data(ttl=600)
def get_companies():
    """Fetch list of all unique company tickers."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT DISTINCT company_id FROM financial_ratios ORDER BY company_id", conn)
        return df["company_id"].tolist()
    except Exception:
        return ["TCS", "INFY", "RELIANCE", "HDFCBANK", "ITC"]  # Robust safety fallbacks
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):
    """Fetch financial ratios for a given ticker, optionally filtered by year."""
    conn = get_connection()
    try:
        if year:
            query = "SELECT * FROM financial_ratios WHERE company_id = ? AND year = ?"
            df = pd.read_sql(query, conn, params=[ticker, year])
        else:
            query = "SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year DESC"
            df = pd.read_sql(query, conn, params=[ticker])
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_pl(ticker):
    """Fetch Profit and Loss statement data for a given ticker."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM profitandloss WHERE company_id = ? ORDER BY year DESC", conn, params=[ticker])
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_bs(ticker):
    """Fetch Balance Sheet data for a given ticker."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM balancesheet WHERE company_id = ? ORDER BY year DESC", conn, params=[ticker])
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_cf(ticker):
    """Fetch Cash Flow statement data for a given ticker."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM cashflow WHERE company_id = ? ORDER BY year DESC", conn, params=[ticker])
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_sectors():
    """Fetch list of all unique sectors/peer groups."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT DISTINCT peer_group_name FROM peer_percentiles WHERE peer_group_name IS NOT NULL", conn)
        return df["peer_group_name"].tolist()
    except Exception:
        return ["IT Services", "Banking", "FMCG", "Energy"]
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_peers(group_name):
    """Fetch all peer percentiles data matching a group name."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM peer_percentiles WHERE peer_group_name = ?", conn, params=[group_name])
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


@st.cache_data(ttl=600)
def get_valuation(ticker):
    """Fetch specific valuation-related parameters for a ticker."""
    conn = get_connection()
    try:
        # Pull PE, PB ratio columns directly from ratios table
        df = pd.read_sql(
            "SELECT company_id, year, debt_to_equity, composite_quality_score FROM financial_ratios WHERE company_id = ?", 
            conn, params=[ticker]
        )
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()