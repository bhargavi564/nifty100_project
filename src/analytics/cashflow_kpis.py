import pandas as pd
from pathlib import Path

Path("output").mkdir(exist_ok=True)
cashflow = pd.read_csv("data/processed/cashflow.csv")
profit = pd.read_csv("data/processed/profitandloss.csv")

def free_cash_flow(cfo, cfi):
    return cfo + cfi
def cfo_quality(cfo, pat):

    if pat == 0:
        return None

    score = cfo / pat

    return score
def quality_label(score):

    if score is None:
        return "N/A"

    if score > 1:
        return "High Quality"

    elif score >= 0.5:
        return "Moderate"

    else:
        return "Accrual Risk"

def capex_intensity(cfi, sales):

    if sales == 0:
        return None

    return abs(cfi) / sales * 100
def capex_label(value):

    if value is None:
        return "N/A"

    if value < 3:
        return "Asset Light"

    elif value <= 8:
        return "Moderate"

    else:
        return "Capital Intensive"
def fcf_conversion(fcf, operating_profit):

    if operating_profit == 0:
        return None

    return fcf / operating_profit * 100
def sign(value):

    if value >= 0:
        return "+"

    return "-"
def capital_pattern(cfo, cfi, cff):

    pattern = (
        sign(cfo),
        sign(cfi),
        sign(cff)
    )

    mapping = {

        ("+","-","-"):
        "Reinvestor",

        ("+","-","+"):
        "Mixed",

        ("+","+","+"):
        "Cash Accumulator",

        ("-","+","+"):
        "Distress Signal",

        ("-","-","+"):
        "Growth Funded by Debt",

        ("+","+","-"):
        "Liquidating Assets",

        ("-","-","-"):
        "Pre-Revenue"

    }

    return mapping.get(pattern,"Unknown")

records=[]
for i,row in cashflow.iterrows():

    pattern = capital_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"]
    )

    records.append({

        "company_id":
        row["company_id"],

        "year":
        row["year"],

        "cfo_sign":
        sign(row["operating_activity"]),

        "cfi_sign":
        sign(row["investing_activity"]),

        "cff_sign":
        sign(row["financing_activity"]),

        "pattern_label":
        pattern

    })
pd.DataFrame(records).to_csv(

"output/capital_allocation.csv",

index=False

)
print("Cash Flow KPIs Completed Successfully")
print("capital_allocation.csv generated Completed Successfully")
print("Pattern Classification Completed Successfully")