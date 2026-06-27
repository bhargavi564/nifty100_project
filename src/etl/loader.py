import pandas as pd
from pathlib import Path

RAW_FOLDER=Path("data/raw")
PROCESSED_FOLDER=Path("data/processed")
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

for file in files:
              df=pd.read_excel(RAW_FOLDER/ file)
              print(file)
print(df.head())


def normalize(df):
              
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df

for file in files:
              
    df=df.drop_duplicates()
    
    df=df.dropna(how="all")
    
    df=df.fillna("")
    
    df = pd.read_excel(RAW_FOLDER / file)

    df = normalize(df)

    output = file.replace(".xlsx", ".csv")

    df.to_csv(
        PROCESSED_FOLDER / output,
        index=False
    )

    print(f"{output} saved")
    
    print(df.shape)