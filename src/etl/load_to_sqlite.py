import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/nifty100.db")

TABLES = [

    "companies",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "profitandloss",
    "prosandcons",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "sectors",
    "stock_prices"

]


def load_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    schema = open("sql/schema.sql").read()

    cursor.executescript(schema)

    audit=[]

    for table in TABLES:

        path=f"data/processed/{table}.csv"

        df=pd.read_csv(path)

        df.to_sql(
            table,
            conn,
            if_exists="replace",
            index=False
        )

        audit.append({
            "table":table,
            "rows_loaded":len(df)
        })

        print(table,"Loaded")

    pd.DataFrame(audit).to_csv(
        "output/load_audit.csv",
        index=False
    )

    conn.commit()
    conn.close()

    print("Database Loaded Successfully")


if __name__ == "__main__":
    load_database()