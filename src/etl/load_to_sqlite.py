import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH=Path("data/nifty100.db")
conn=sqlite3.connect(DB_PATH)
print("Database Created")

conn.execute("PRAGMA foreign_keys= ON")
cursor=conn.cursor()

schema=open("sql/schema.sql").read()
cursor.executescript(schema)
print("Tables Created")

companies=pd.read_csv("data/processed/companies.csv")
companies.to_sql("companies",conn,if_exists="replace",index=False)

files = [

"companies",

"balancesheet",

"cashflow",

"analysis",

"documents",

"profitandloss",

"prosandcons",

"financial_ratios",

"peer_groups",

"stock_prices"

]

for table in files:
              
    df = pd.read_csv(
        f"data/processed/{table}.csv"
    )

    df.to_sql(
        table,
        conn,
        if_exists="replace",
        index=False
    )

    print(f"{table} Loaded")
    
conn = sqlite3.connect("data/nifty100.db")

cursor = conn.cursor()

tables = [

"companies",

"balancesheet",

"cashflow",

"analysis",

"documents",

"profitandloss",

"prosandcons",

"financial_ratios",

"peer_groups",

"stock_prices"

]

for table in tables:

    cursor.execute(f"SELECT COUNT(*) FROM {table}")

    rows = cursor.fetchone()[0]

    print(table, rows)
    
conn.commit()
conn.close()
print("Database Ready")