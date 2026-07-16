import os
import sqlite3
from pathlib import Path
import pandas as pd

from ratios import net_profit_margin, operating_profit_margin, roe
from leverage import debt_to_equity, interest_coverage, asset_turnover
from cashflow_kpis import free_cash_flow, capex_intensity, capital_pattern, sign
from cagr import revenue_cagr, pat_cagr, eps_cagr

# 1. Dynamically find project root ('sprint1') and database path
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"

# Connect to the correct database
conn = sqlite3.connect(str(DB_PATH))

# ------------------------------------
# Read Tables
# ------------------------------------
profit = pd.read_sql("SELECT * FROM profitandloss", conn)
balance = pd.read_sql("SELECT * FROM balancesheet", conn)
cashflow = pd.read_sql("SELECT * FROM cashflow", conn)

# ------------------------------------
# Merge Tables
# ------------------------------------
df = profit.merge(balance, on=["company_id", "year"], how="left")
df = df.merge(cashflow, on=["company_id", "year"], how="left")

# ------------------------------------
# Day 8 Ratios
# ------------------------------------
df["net_profit_margin_pct"] = df.apply(
    lambda x: net_profit_margin(x["net_profit"], x["sales"]), axis=1
)

df["operating_profit_margin_pct"] = df.apply(
    lambda x: operating_profit_margin(x["operating_profit"], x["sales"]), axis=1
)

df["return_on_equity_pct"] = df.apply(
    lambda x: roe(x["net_profit"], x["equity_capital"], x["reserves"]), axis=1
)

# ------------------------------------
# Day 9 Ratios
# ------------------------------------
df["debt_to_equity"] = df.apply(
    lambda x: debt_to_equity(x["borrowings"], x["equity_capital"], x["reserves"]),
    axis=1,
)

df["interest_coverage"] = df.apply(
    lambda x: interest_coverage(
        x["operating_profit"], x["other_income"], x["interest"]
    ),
    axis=1,
)

df["asset_turnover"] = df.apply(
    lambda x: asset_turnover(x["sales"], x["total_assets"]), axis=1
)

# ------------------------------------
# Day 11 Ratios
# ------------------------------------
df["free_cash_flow"] = df.apply(
    lambda x: free_cash_flow(x["operating_activity"], x["investing_activity"]),
    axis=1,
)

df["capex_cr"] = df.apply(
    lambda x: capex_intensity(x["investing_activity"], x["sales"]), axis=1
)

# ------------------------------------
# Day 10 CAGR
# ------------------------------------
df["revenue_cagr_5yr"] = None
df["pat_cagr_5yr"] = None
df["eps_cagr_5yr"] = None

for company in df["company_id"].unique():
    company_df = df[df["company_id"] == company].sort_values("year")

    if len(company_df) >= 5:
        start = company_df.iloc[0]
        end = company_df.iloc[-1]

        rev, _ = revenue_cagr(start["sales"], end["sales"], 5)
        pat, _ = pat_cagr(start["net_profit"], end["net_profit"], 5)
        eps, _ = eps_cagr(start["eps"], end["eps"], 5)

        df.loc[df["company_id"] == company, "revenue_cagr_5yr"] = rev
        df.loc[df["company_id"] == company, "pat_cagr_5yr"] = pat
        df.loc[df["company_id"] == company, "eps_cagr_5yr"] = eps

# ------------------------------------
# Placeholder Columns
# ------------------------------------
df["earnings_per_share"] = df.get("eps", None)
df["book_value_per_share"] = None
df["dividend_payout_ratio_pct"] = None
df["total_debt_cr"] = df.get("borrowings", None)
df["cash_from_operations_cr"] = df.get("operating_activity", None)

# ------------------------------------
# Composite Score
# ------------------------------------
df["composite_quality_score"] = (
    df["net_profit_margin_pct"].fillna(0)
    + df["operating_profit_margin_pct"].fillna(0)
    + df["return_on_equity_pct"].fillna(0)
) / 3

# ------------------------------------
# Final Table Generation
# ------------------------------------
df = df.drop_duplicates(subset=["company_id", "year"])

ratios = df[
    [
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score",
    ]
]

ratios.to_sql("financial_ratios", conn, if_exists="replace", index=False)
print("Rows Inserted into financial_ratios:", len(ratios))
print("Financial Ratios Table Populated Successfully")

# ------------------------------------
# Capital Allocation Patterns
# ------------------------------------
records = []
for i, row in cashflow.iterrows():
    pattern = capital_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"],
    )

    records.append(
        {
            "company_id": row["company_id"],
            "year": row["year"],
            "cfo_sign": sign(row["operating_activity"]),
            "cfi_sign": sign(row["investing_activity"]),
            "cff_sign": sign(row["financing_activity"]),
            "pattern_label": pattern,
        }
    )

# Ensure the output folder exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
output_csv_path = OUTPUT_DIR / "capital_allocation.csv"

pd.DataFrame(records).to_csv(output_csv_path, index=False)
print("Cash Flow KPIs Completed Successfully")

conn.commit()
conn.close()