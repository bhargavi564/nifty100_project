import pandas as pd
from pathlib import Path

RAW_FOLDER = Path("data/raw")
PROCESSED_FOLDER = Path("data/processed")
PROCESSED_FOLDER.mkdir(exist_ok=True)

files = [
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


def normalize(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


for file in files:

    if file == "companies.xlsx":
        df = pd.read_excel(RAW_FOLDER / file, header=1)
    else:
        df = pd.read_excel(RAW_FOLDER / file, header=0)

    df = normalize(df)

    df.drop_duplicates(inplace=True)
    df.dropna(how="all", inplace=True)
    df=df.astype(str)
    df=df.fillna("")

    output = file.replace(".xlsx", ".csv")

    df.to_csv(
        PROCESSED_FOLDER / output,
        index=False
    )

    print(output, "saved")
  