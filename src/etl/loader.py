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

header_map = {
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

for file in files:
    df = pd.read_excel(
        RAW_FOLDER / file,
        header=header_map[file]
    )
    print(f"\n{file}")
    print("Shape:",df.shape)
    print("Columns:",list(df.columns))
    
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