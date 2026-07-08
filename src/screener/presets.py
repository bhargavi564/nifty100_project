import sqlite3
import pandas as pd
from pathlib import Path

from engine import apply_filters

# -----------------------------------
# Database Path
# -----------------------------------

DB_PATH = Path("data/nifty100.db")


# -----------------------------------
# Load Financial Ratios
# -----------------------------------

def load_financial_ratios():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    conn.close()

    return df


# -----------------------------------
# 1. Quality Compounder
# ROE > 15%
# D/E < 1
# FCF > 0
# Revenue CAGR > 10%
# -----------------------------------

def quality_compounder():

    config = {
        "roe_min": 15,
        "debt_to_equity_max": 1,
        "fcf_min": 0,
        "revenue_cagr_5yr_min": 10
    }

    return apply_filters(load_financial_ratios(), config)


# -----------------------------------
# 2. Value Pick
# PE < 20
# PB < 3
# D/E < 2
# Dividend Yield > 1%
# -----------------------------------

def value_pick():

    config = {
        "pe_max": 20,
        "pb_max": 3,
        "debt_to_equity_max": 2,
        "dividend_yield_min": 1
    }

    return apply_filters(load_financial_ratios(), config)


# -----------------------------------
# 3. Growth Accelerator
# PAT CAGR > 20%
# Revenue CAGR > 15%
# D/E < 2
# -----------------------------------

def growth_accelerator():

    config = {
        "pat_cagr_5yr_min": 20,
        "revenue_cagr_5yr_min": 15,
        "debt_to_equity_max": 2
    }

    return apply_filters(load_financial_ratios(), config)


# -----------------------------------
# 4. Dividend Champion
# Dividend Yield > 2%
# Dividend Payout < 80%
# FCF > 0
# -----------------------------------

def dividend_champion():

    config = {
        "dividend_yield_min": 2,
        "dividend_payout_ratio_pct_max": 80,
        "fcf_min": 0
    }

    return apply_filters(load_financial_ratios(), config)


# -----------------------------------
# 5. Debt Free Blue Chip
# D/E = 0
# ROE > 12%
# Sales > 5000
# -----------------------------------

def debt_free_bluechip():

    config = {
        "debt_to_equity_max": 0,
        "roe_min": 12,
        "sales_min": 5000
    }

    return apply_filters(load_financial_ratios(), config)


# -----------------------------------
# 6. Turnaround Watch
# Revenue CAGR > 10%
# FCF > 0
# -----------------------------------

def turnaround_watch():

    config = {
        "revenue_cagr_5yr_min": 10,
        "fcf_min": 0
    }

    result = apply_filters(load_financial_ratios(), config)

    if "company_id" in result.columns and "year" in result.columns:
        result = result.sort_values(
            by=["company_id", "year"]
        )

    return result.reset_index(drop=True)


# -----------------------------------
# Display Results
# -----------------------------------

def main():

    presets = {
        "Quality Compounder": quality_compounder(),
        "Value Pick": value_pick(),
        "Growth Accelerator": growth_accelerator(),
        "Dividend Champion": dividend_champion(),
        "Debt Free Blue Chip": debt_free_bluechip(),
        "Turnaround Watch": turnaround_watch()
    }

    for name, df in presets.items():

        print("\n" + "=" * 60)
        print(name)
        print("=" * 60)
        print(f"Companies Found : {len(df)}")
        print(df.head())


if __name__ == "__main__":
    main()