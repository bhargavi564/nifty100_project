import sqlite3
import pandas as pd
import yaml
from pathlib import Path

# -----------------------------------
# Paths
# -----------------------------------

DB_PATH = Path("data/nifty100.db")
CONFIG_PATH = Path("config/screener_config.yaml")
OUTPUT_PATH = Path("output/screener_results.csv")


# -----------------------------------
# Load YAML Config
# -----------------------------------

def load_config():
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file)


# -----------------------------------
# Load Financial Ratios
# -----------------------------------

def load_data():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    conn.close()

    return df


# -----------------------------------
# Apply Filters
# -----------------------------------

def apply_filters(df, config):

    df = df.copy()

    # ROE
    if "return_on_equity_pct" in df.columns:
        df = df[
            df["return_on_equity_pct"] >= config.get("roe_min", 0)
        ]

    # Debt to Equity
    if "debt_to_equity" in df.columns:

        if "broad_sector" in df.columns:

            financial_mask = (
                df["broad_sector"]
                .fillna("")
                .str.lower()
                .eq("financials")
            )

            df = df[
                financial_mask |
                (df["debt_to_equity"] <= config.get("debt_to_equity_max", 999999))
            ]

        else:

            df = df[
                df["debt_to_equity"] <= config.get("debt_to_equity_max", 999999)
            ]

    # Free Cash Flow
    if "free_cash_flow" in df.columns:
        df = df[
            df["free_cash_flow"] >= config.get("fcf_min", -999999)
        ]

    # Revenue CAGR
    if "revenue_cagr_5yr" in df.columns:
        df = df[
            df["revenue_cagr_5yr"] >= config.get("revenue_cagr_5yr_min", -999999)
        ]

    # PAT CAGR
    if "pat_cagr_5yr" in df.columns:
        df = df[
            df["pat_cagr_5yr"] >= config.get("pat_cagr_5yr_min", -999999)
        ]

    # EPS CAGR
    if "eps_cagr_5yr" in df.columns:
        df = df[
            df["eps_cagr_5yr"] >= config.get("eps_cagr_min", -999999)
        ]

    # Operating Profit Margin
    if "operating_profit_margin_pct" in df.columns:
        df = df[
            df["operating_profit_margin_pct"] >= config.get("opm_min", -999999)
        ]

    # Interest Coverage
    if "interest_coverage" in df.columns:

        if "icr_label" in df.columns:

            debt_free = (
                df["icr_label"]
                .fillna("")
                .str.lower()
                .eq("debt free")
            )

            df = df[
                debt_free |
                (df["interest_coverage"] >= config.get("icr_min", 0))
            ]

        else:

            df = df[
                df["interest_coverage"] >= config.get("icr_min", 0)
            ]

    # Market Cap
    if "market_cap" in df.columns:
        df = df[
            df["market_cap"] >= config.get("market_cap_min", 0)
        ]

    # Net Profit
    if "net_profit" in df.columns:
        df = df[
            df["net_profit"] >= config.get("net_profit_min", 0)
        ]

    # Asset Turnover
    if "asset_turnover" in df.columns:
        df = df[
            df["asset_turnover"] >= config.get("asset_turnover_min", 0)
        ]

    # Sales
    if "sales" in df.columns:
        df = df[
            df["sales"] >= config.get("sales_min", 0)
        ]

    # PE Ratio
    if "pe_ratio" in df.columns:
        df = df[
            df["pe_ratio"] <= config.get("pe_max", 999999)
        ]

    # PB Ratio
    if "price_to_book" in df.columns:
        df = df[
            df["price_to_book"] <= config.get("pb_max", 999999)
        ]

    # Dividend Yield
    if "dividend_yield" in df.columns:
        df = df[
            df["dividend_yield"] >= config.get("dividend_yield_min", 0)
        ]

    # Dividend Payout Ratio
    if "dividend_payout_ratio_pct" in df.columns:
        df = df[
            df["dividend_payout_ratio_pct"]
            <= config.get("dividend_payout_ratio_pct_max", 100)
        ]

    # Composite Score Sorting
    if "composite_quality_score" in df.columns:
        df = df.sort_values(
            by="composite_quality_score",
            ascending=False
        )

    return df.reset_index(drop=True)


# -----------------------------------
# Main
# -----------------------------------

def main():

    print("Loading Configuration...")

    config = load_config()

    print("Loading Financial Ratios...")

    df = load_data()

    print("Applying Filters...")

    result = apply_filters(df, config)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nFiltering Completed Successfully")
    print(f"Matching Companies : {len(result)}")
    print(f"Output Saved : {OUTPUT_PATH}")

    print("\nTop Results\n")
    print(result.head())


if __name__ == "__main__":
    main()