"""
loader.py

Purpose:
Read all raw Excel files, clean them using normaliser.py,
and save them as CSV files in data/processed.
"""

import pandas as pd
from pathlib import Path
from normaliser import clean_dataframe

# Folder paths
RAW_FOLDER = Path("data/raw")
PROCESSED_FOLDER = Path("data/processed")

# Create processed folder if it doesn't exist
PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

# Excel files
FILES = [
    "companies.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "profitandloss.xlsx",
    "prosandcons.xlsx",
    "financial_ratios.xlsx",
    "market_cap.xlsx",
    "peer_groups.xlsx",
    "sectors.xlsx",
    "stock_prices.xlsx"
]

# Header row mapping
HEADER_MAP = {
    "companies.xlsx": 1,
    "balancesheet.xlsx": 1,
    "cashflow.xlsx": 1,
    "analysis.xlsx": 1,
    "documents.xlsx": 1,
    "profitandloss.xlsx": 1,
    "prosandcons.xlsx": 1,
    "financial_ratios.xlsx": 0,
    "market_cap.xlsx": 0,
    "peer_groups.xlsx": 0,
    "sectors.xlsx": 0,
    "stock_prices.xlsx": 0
}


def load_all_files():
    """
    Read every Excel file, clean it,
    and save as CSV.
    """

    print("=" * 60)
    print("Starting Excel Loader")
    print("=" * 60)

    for file in FILES:

        try:
            print(f"\nReading: {file}")

            # Read Excel
            df = pd.read_excel(
                RAW_FOLDER / file,
                header=HEADER_MAP[file]
            )

            print(f"Original Shape: {df.shape}")

            # Clean DataFrame
            df = clean_dataframe(df)

            print(f"Cleaned Shape : {df.shape}")

            # Save CSV
            output_file = file.replace(".xlsx", ".csv")

            df.to_csv(
                PROCESSED_FOLDER / output_file,
                index=False
            )

            print(f"Saved: {output_file}")

        except Exception as e:
            print(f"Error processing {file}")
            print(e)

    print("\n" + "=" * 60)
    print("All files processed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    load_all_files()