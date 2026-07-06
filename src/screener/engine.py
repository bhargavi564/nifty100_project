import sqlite3
import pandas as pd
import yaml
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
DB_PATH = Path("data/nifty100.db")
CONFIG_PATH = Path("config/screener_config.yaml")
OUTPUT_PATH = Path("output/screener_results.csv")


# -----------------------------
# Load Configuration
# -----------------------------
def load_config():
    print("Loading screener configuration...\n")

    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)

    return config


# -----------------------------
# Load Financial Ratios Table
# -----------------------------
def load_data():
    print("Connecting to SQLite database...\n")

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    conn.close()

    print("Loaded financial_ratios table.\n")

    return df


# -----------------------------
# Main
# -----------------------------
def main():

    config = load_config()

    df = load_data()

    # ---------------- ROE ----------------
    if "return_on_equity_pct" in df.columns:
        df = df[
            df["return_on_equity_pct"] >= config["roe_min"]
        ]
    print("Applied ROE filter.")

    # ---------------- Debt To Equity ----------------
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
                (df["debt_to_equity"] <= config["debt_to_equity_max"])
            ]

        else:

            df = df[
                df["debt_to_equity"] <= config["debt_to_equity_max"]
            ]

    print("Applied Debt-to-Equity filter.")

    # ---------------- Revenue CAGR ----------------
    if "revenue_cagr_5yr" in df.columns:
        df = df[
            df["revenue_cagr_5yr"] >= config["revenue_cagr_5yr_min"]
        ]

    print("Applied Revenue CAGR filter.")

    # ---------------- PAT CAGR ----------------
    if "pat_cagr_5yr" in df.columns:
        df = df[
            df["pat_cagr_5yr"] >= config["pat_cagr_5yr_min"]
        ]

    print("Applied PAT CAGR filter.")

    # ---------------- Operating Margin ----------------
    if "operating_profit_margin_pct" in df.columns:
        df = df[
            df["operating_profit_margin_pct"] >= config["opm_min"]
        ]

    print("Applied OPM filter.")

    # ---------------- PE ----------------
    if "pe" in df.columns:
        df = df[
            df["pe"] <= config["pe_max"]
        ]

    # ---------------- PB ----------------
    if "pb" in df.columns:
        df = df[
            df["pb"] <= config["pb_max"]
        ]

    print("Applied PE/PB filters.")

    # ---------------- Dividend Yield ----------------
    if "dividend_yield" in df.columns:
        df = df[
            df["dividend_yield"] >= config["dividend_yield_min"]
        ]

    print("Applied Dividend Yield filter.")

    # ---------------- Interest Coverage ----------------
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
                (df["interest_coverage"] >= config["icr_min"])
            ]

        else:

            df = df[
                df["interest_coverage"] >= config["icr_min"]
            ]

    print("Applied Interest Coverage filter.")

    # ---------------- Market Cap ----------------
    if "market_cap" in df.columns:
        df = df[
            df["market_cap"] >= config["market_cap_min"]
        ]

    print("Applied Market Cap filter.")

    # ---------------- Net Profit ----------------
    if "net_profit" in df.columns:
        df = df[
            df["net_profit"] >= config["net_profit_min"]
        ]

    print("Applied Net Profit filter.")

    # ---------------- EPS CAGR ----------------
    if "eps_cagr_5yr" in df.columns:
        df = df[
            df["eps_cagr_5yr"] >= config["eps_cagr_min"]
        ]

    print("Applied EPS CAGR filter.")

    # ---------------- Asset Turnover ----------------
    if "asset_turnover" in df.columns:
        df = df[
            df["asset_turnover"] >= config["asset_turnover_min"]
        ]

    print("Applied Asset Turnover filter.")

    # ---------------- Sales ----------------
    if "sales" in df.columns:
        df = df[
            df["sales"] >= config["sales_min"]
        ]

    print("Applied Sales filter.")

    # ---------------- Free Cash Flow ----------------
    if "free_cash_flow" in df.columns:
        df = df[
            df["free_cash_flow"] >= config["fcf_min"]
        ]

    print("Applied Free Cash Flow filter.")

    # ---------------- Sort ----------------
    if "composite_quality_score" in df.columns:

        df = df.sort_values(
            by="composite_quality_score",
            ascending=False
        )

    print("Sorted companies by Composite Quality Score.")

    # ---------------- Save ----------------
    OUTPUT_PATH.parent.mkdir(exist_ok=True)

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nFiltering Completed Successfully.\n")

    print(f"Matching Companies: {len(df)}")

    print("\nResults saved to:")
    print(OUTPUT_PATH)

    print("\nTop 10 Companies:\n")
    print(df.head(10))


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    main()