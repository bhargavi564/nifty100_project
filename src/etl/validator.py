import pandas as pd
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
DATA_FOLDER = Path("data/processed")
OUTPUT_FOLDER = Path("output")
OUTPUT_FOLDER.mkdir(exist_ok=True)

# -----------------------------
# Load CSV Files
# -----------------------------
companies = pd.read_csv(DATA_FOLDER / "companies.csv")
sectors = pd.read_csv(DATA_FOLDER / "sectors.csv")
ratios = pd.read_csv(DATA_FOLDER / "financial_ratios.csv")
balance = pd.read_csv(DATA_FOLDER / "balancesheet.csv")
prices = pd.read_csv(DATA_FOLDER / "stock_prices.csv")

validation_errors = []

# -----------------------------
# DQ-01 Duplicate Company IDs
# -----------------------------
duplicates = companies[companies.duplicated(subset=["id"])]

if len(duplicates) > 0:
    validation_errors.append({
        "Rule": "DQ-01",
        "Severity": "CRITICAL",
        "Message": f"{len(duplicates)} Duplicate Company IDs Found"
    })

# -----------------------------
# DQ-02 Missing Company Name
# -----------------------------
missing = companies["company_name"].isnull().sum()

if missing > 0:
    validation_errors.append({
        "Rule": "DQ-02",
        "Severity": "CRITICAL",
        "Message": f"{missing} Missing Company Names"
    })

# -----------------------------
# DQ-03 Missing Broad Sector
# -----------------------------
missing = sectors["broad_sector"].isnull().sum()

if missing > 0:
    validation_errors.append({
        "Rule": "DQ-03",
        "Severity": "WARNING",
        "Message": f"{missing} Missing Broad Sector"
    })

# -----------------------------
# DQ-04 Duplicate Company Name
# -----------------------------
duplicates = companies[
    companies.duplicated(subset=["company_name"])
]

if len(duplicates) > 0:
    validation_errors.append({
        "Rule": "DQ-04",
        "Severity": "WARNING",
        "Message": f"{len(duplicates)} Duplicate Company Names"
    })

# -----------------------------
# DQ-05 Empty Rows
# -----------------------------
empty_rows = companies.isnull().all(axis=1).sum()

if empty_rows > 0:
    validation_errors.append({
        "Rule": "DQ-05",
        "Severity": "WARNING",
        "Message": f"{empty_rows} Empty Rows"
    })

# -----------------------------
# DQ-06 Invalid ROE
# -----------------------------
if "roe_percentage" in ratios.columns:

    ratios["roe_percentage"] = pd.to_numeric(
        ratios["roe_percentage"],
        errors="coerce"
    )

    invalid = ratios["roe_percentage"].isnull().sum()

    if invalid > 0:
        validation_errors.append({
            "Rule": "DQ-06",
            "Severity": "WARNING",
            "Message": f"{invalid} Invalid ROE Values"
        })

# -----------------------------
# DQ-07 Negative Assets
# -----------------------------
if "assets" in balance.columns:

    negative = balance[balance["assets"] < 0]

    if len(negative) > 0:
        validation_errors.append({
            "Rule": "DQ-07",
            "Severity": "CRITICAL",
            "Message": f"{len(negative)} Negative Assets"
        })

# -----------------------------
# DQ-08 Invalid Stock Price
# -----------------------------
if "close" in prices.columns:

    negative = prices[prices["close"] <= 0]

    if len(negative) > 0:
        validation_errors.append({
            "Rule": "DQ-08",
            "Severity": "CRITICAL",
            "Message": f"{len(negative)} Invalid Closing Prices"
        })

# -----------------------------
# DQ-09 Invalid Date
# -----------------------------
if "date" in prices.columns:

    prices["date"] = pd.to_datetime(
        prices["date"],
        errors="coerce"
    )

    invalid = prices["date"].isnull().sum()

    if invalid > 0:
        validation_errors.append({
            "Rule": "DQ-09",
            "Severity": "WARNING",
            "Message": f"{invalid} Invalid Dates"
        })

# -----------------------------
# DQ-10 Invalid Company IDs
# -----------------------------
if "company_id" in prices.columns:

    invalid = prices[
        ~prices["company_id"].isin(sectors["company_id"])
    ]

    if len(invalid) > 0:
        validation_errors.append({
            "Rule": "DQ-10",
            "Severity": "WARNING",
            "Message": f"{len(invalid)} Invalid Company IDs"
        })

# -----------------------------
# Save Report
# -----------------------------
report = pd.DataFrame(
    validation_errors,
    columns=["Rule", "Severity", "Message"]
)

report.to_csv(
    OUTPUT_FOLDER / "validation_failures.csv",
    index=False
)

print("\nValidation Completed")
print(report)