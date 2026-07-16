from pathlib import Path
import sys
import pandas as pd
import numpy as np

# Resolve project paths safely
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _clean_numeric_col(df: pd.DataFrame, col: str) -> pd.Series:
    """Safely converts a column to numeric, returning NaNs if column doesn't exist."""
    if col not in df.columns:
        return pd.Series(np.nan, index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def _first_existing_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Returns the first column name found in the DataFrame from a list of candidates."""
    return next((col for col in candidates if col in df.columns), None)


def _apply_mask_and_sort(df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    """Filters the DataFrame using the boolean mask and sorts by quality score if present."""
    result = df.loc[mask.fillna(False)].copy()
    if "composite_quality_score" in result.columns:
        result = result.sort_values("composite_quality_score", ascending=False)
    return result


# =====================================================================
# Stock Screening Strategies
# =====================================================================

def quality_compounder(df: pd.DataFrame) -> pd.DataFrame:
    """Filters for high-return, low-debt, cash-generating compounders."""
    mask = pd.Series(True, index=df.index)

    if "return_on_equity_pct" in df.columns:
        mask &= _clean_numeric_col(df, "return_on_equity_pct") > 15
    if "debt_to_equity" in df.columns:
        mask &= _clean_numeric_col(df, "debt_to_equity") < 1
    if "free_cash_flow_cr" in df.columns:
        mask &= _clean_numeric_col(df, "free_cash_flow_cr") > 0
    if "revenue_cagr_5yr" in df.columns:
        mask &= _clean_numeric_col(df, "revenue_cagr_5yr") > 10

    return _apply_mask_and_sort(df, mask)


def value_pick(df: pd.DataFrame) -> pd.DataFrame:
    """Filters for fundamentally strong, reasonably valued stocks."""
    mask = pd.Series(True, index=df.index)

    if "price_to_earnings" in df.columns:
        mask &= _clean_numeric_col(df, "price_to_earnings") < 20
    if "price_to_book" in df.columns:
        mask &= _clean_numeric_col(df, "price_to_book") < 3
    if "debt_to_equity" in df.columns:
        mask &= _clean_numeric_col(df, "debt_to_equity") < 2
    if "dividend_yield_pct" in df.columns:
        mask &= _clean_numeric_col(df, "dividend_yield_pct") > 1

    return _apply_mask_and_sort(df, mask)


def growth_accelerator(df: pd.DataFrame) -> pd.DataFrame:
    """Filters for high-growth firms with manageable leverage."""
    mask = pd.Series(True, index=df.index)

    if "pat_cagr_5yr" in df.columns:
        mask &= _clean_numeric_col(df, "pat_cagr_5yr") > 20
    if "revenue_cagr_5yr" in df.columns:
        mask &= _clean_numeric_col(df, "revenue_cagr_5yr") > 15
    if "debt_to_equity" in df.columns:
        mask &= _clean_numeric_col(df, "debt_to_equity") < 2

    return _apply_mask_and_sort(df, mask)


def dividend_champion(df: pd.DataFrame) -> pd.DataFrame:
    """Filters for stable dividend-paying stocks with secure payouts."""
    mask = pd.Series(True, index=df.index)

    if "dividend_yield_pct" in df.columns:
        mask &= _clean_numeric_col(df, "dividend_yield_pct") > 2
    if "dividend_payout_ratio_pct" in df.columns:
        mask &= _clean_numeric_col(df, "dividend_payout_ratio_pct") < 80
    if "free_cash_flow_cr" in df.columns:
        mask &= _clean_numeric_col(df, "free_cash_flow_cr") > 0

    return _apply_mask_and_sort(df, mask)


def debt_free_bluechip(df: pd.DataFrame) -> pd.DataFrame:
    """Filters for large, highly profitable companies with zero debt."""
    mask = pd.Series(True, index=df.index)

    if "debt_to_equity" in df.columns:
        mask &= _clean_numeric_col(df, "debt_to_equity") == 0
    if "return_on_equity_pct" in df.columns:
        mask &= _clean_numeric_col(df, "return_on_equity_pct") > 12

    revenue_col = _first_existing_col(df, ["revenue_cr", "sales_cr", "sales", "revenue"])
    if revenue_col is not None:
        mask &= _clean_numeric_col(df, revenue_col) > 5000

    return _apply_mask_and_sort(df, mask)


def turnaround_watch(df: pd.DataFrame) -> pd.DataFrame:
    """Filters for cash-generating companies showing improving debt dynamics."""
    mask = pd.Series(True, index=df.index)

    if "revenue_cagr_3yr" in df.columns:
        mask &= _clean_numeric_col(df, "revenue_cagr_3yr") > 10
    if "free_cash_flow_cr" in df.columns:
        mask &= _clean_numeric_col(df, "free_cash_flow_cr") > 0

    if "debt_to_equity_yoy_change" in df.columns:
        mask &= _clean_numeric_col(df, "debt_to_equity_yoy_change") < 0
    elif "debt_to_equity_prev" in df.columns and "debt_to_equity" in df.columns:
        de_current = _clean_numeric_col(df, "debt_to_equity")
        de_prev = _clean_numeric_col(df, "debt_to_equity_prev")
        mask &= de_current < de_prev

    return _apply_mask_and_sort(df, mask)


# =====================================================================
# Execution Block: Triggered when running "python src/screener/presets.py"
# =====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Running Presets Stock Screeners Demo...")
    print("=" * 60)

    # 1. Create a dummy dataset mimicking Nifty 100 metrics
    sample_data = {
        "ticker": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ITC", "TATASTEEL"],
        "return_on_equity_pct": [16.5, 38.2, 29.1, 14.1, 25.4, 8.5],
        "debt_to_equity": [0.38, 0.02, 0.00, 0.95, 0.00, 1.2],
        "free_cash_flow_cr": [12000, 32000, 21000, -5000, 15000, -2000],
        "revenue_cagr_5yr": [12.5, 14.1, 11.8, 18.2, 8.5, 5.1],
        "price_to_earnings": [24.5, 28.1, 21.0, 19.5, 26.3, 11.2],
        "price_to_book": [2.8, 8.5, 6.2, 2.5, 5.1, 1.1],
        "dividend_yield_pct": [0.8, 2.1, 2.5, 1.1, 3.8, 2.2],
        "dividend_payout_ratio_pct": [20.0, 65.0, 55.0, 22.0, 75.0, 45.0],
        "revenue_cr": [850000, 220000, 150000, 200000, 70000, 130000],
        "composite_quality_score": [85, 98, 92, 75, 88, 50],
    }
    df_stocks = pd.DataFrame(sample_data)

    # 2. Run Screeners and Display the Outputs
    print("\n--- Strategy: Quality Compounders ---")
    quality_df = quality_compounder(df_stocks)
    print(quality_df[["ticker", "return_on_equity_pct", "debt_to_equity", "free_cash_flow_cr", "composite_quality_score"]])

    print("\n--- Strategy: Debt-Free Bluechips ---")
    bluechip_df = debt_free_bluechip(df_stocks)
    print(bluechip_df[["ticker", "debt_to_equity", "return_on_equity_pct", "revenue_cr"]])

    print("\n--- Strategy: Dividend Champions ---")
    dividend_df = dividend_champion(df_stocks)
    print(dividend_df[["ticker", "dividend_yield_pct", "dividend_payout_ratio_pct", "free_cash_flow_cr"]])
    print("=" * 60)