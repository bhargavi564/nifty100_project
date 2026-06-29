import pandas as pd
from pathlib import Path

DATA_FOLDER = Path("data/processed")
OUTPUT_FOLDER = Path("output")
OUTPUT_FOLDER.mkdir(exist_ok=True)


def validate_data():

    companies = pd.read_csv(DATA_FOLDER / "companies.csv")
    sectors = pd.read_csv(DATA_FOLDER / "sectors.csv")
    ratios = pd.read_csv(DATA_FOLDER / "financial_ratios.csv")
    balance = pd.read_csv(DATA_FOLDER / "balancesheet.csv")
    prices = pd.read_csv(DATA_FOLDER / "stock_prices.csv")

    validation_errors = []

    # DQ-01
    duplicates = companies[companies.duplicated(subset=["id"])]

    if len(duplicates) > 0:
        validation_errors.append({
            "Rule":"DQ-01",
            "Severity":"CRITICAL",
            "Message":f"{len(duplicates)} Duplicate Company IDs"
        })

    # DQ-02
    missing = companies["company_name"].isnull().sum()

    if missing > 0:
        validation_errors.append({
            "Rule":"DQ-02",
            "Severity":"CRITICAL",
            "Message":f"{missing} Missing Company Names"
        })

    # DQ-03
    if "broad_sector" in sectors.columns:

        missing = sectors["broad_sector"].isnull().sum()

        if missing > 0:
            validation_errors.append({
                "Rule":"DQ-03",
                "Severity":"WARNING",
                "Message":f"{missing} Missing Broad Sector"
            })

    report = pd.DataFrame(validation_errors)

    report.to_csv(
        OUTPUT_FOLDER/"validation_failures.csv",
        index=False
    )

    print("Validation Completed")

    print(report)


if __name__ == "__main__":
    validate_data()