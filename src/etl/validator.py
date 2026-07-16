import pandas as pd
from pathlib import Path

DATA_FOLDER = Path("data/processed")
OUTPUT_FOLDER = Path("output")
OUTPUT_FOLDER.mkdir(exist_ok=True)


def validate_data():

    print("Running Data Validation...")

    companies = pd.read_csv(DATA_FOLDER / "companies.csv")
    sectors = pd.read_csv(DATA_FOLDER / "sectors.csv")
    ratios = pd.read_csv(DATA_FOLDER / "financial_ratios.csv")
    balance = pd.read_csv(DATA_FOLDER / "balancesheet.csv")
    prices = pd.read_csv(DATA_FOLDER / "stock_prices.csv")

    validation_errors = []

    # -------------------------
    # DQ-01 Duplicate Company IDs
    # -------------------------
    duplicates = companies.duplicated(subset=["id"]).sum()

    if duplicates > 0:
        validation_errors.append({
            "Rule": "DQ-01",
            "Severity": "CRITICAL",
            "Message": f"{duplicates} Duplicate Company IDs"
        })

    # -------------------------
    # DQ-02 Missing Company Name
    # -------------------------
    if "company_name" in companies.columns:

        missing = companies["company_name"].isna().sum()

        if missing > 0:
            validation_errors.append({
                "Rule": "DQ-02",
                "Severity": "CRITICAL",
                "Message": f"{missing} Missing Company Names"
            })

    # -------------------------
    # DQ-03 Missing Broad Sector
    # -------------------------
    if "broad_sector" in sectors.columns:

        missing = sectors["broad_sector"].isna().sum()

        if missing > 0:
            validation_errors.append({
                "Rule": "DQ-03",
                "Severity": "WARNING",
                "Message": f"{missing} Missing Broad Sector"
            })

    # -------------------------
    # DQ-04 Duplicate Company Name
    # -------------------------
    if "company_name" in companies.columns:

        duplicate_names = companies.duplicated(subset=["company_name"]).sum()

        if duplicate_names > 0:
            validation_errors.append({
                "Rule": "DQ-04",
                "Severity": "WARNING",
                "Message": f"{duplicate_names} Duplicate Company Names"
            })

    # -------------------------
    # DQ-05 Empty Rows
    # -------------------------
    empty_rows = companies.isna().all(axis=1).sum()

    if empty_rows > 0:
        validation_errors.append({
            "Rule": "DQ-05",
            "Severity": "WARNING",
            "Message": f"{empty_rows} Empty Rows"
        })

    # -------------------------
    # DQ-06 Invalid ROE
    # -------------------------
    if "roe_percentage" in ratios.columns:

        ratios["roe_percentage"] = pd.to_numeric(
            ratios["roe_percentage"],
            errors="coerce"
        )

        invalid = ratios["roe_percentage"].isna().sum()

        if invalid > 0:
            validation_errors.append({
                "Rule": "DQ-06",
                "Severity": "WARNING",
                "Message": f"{invalid} Invalid ROE Values"
            })

    # -------------------------
    # DQ-07 Negative Assets
    # -------------------------
    if "assets" in balance.columns:

        balance["assets"] = pd.to_numeric(
            balance["assets"],
            errors="coerce"
        )

        negative = (balance["assets"] < 0).sum()

        if negative > 0:
            validation_errors.append({
                "Rule": "DQ-07",
                "Severity": "CRITICAL",
                "Message": f"{negative} Negative Assets"
            })

    # -------------------------
    # DQ-08 Invalid Stock Price
    # -------------------------
    if "close" in prices.columns:

        prices["close"] = pd.to_numeric(
            prices["close"],
            errors="coerce"
        )

        invalid = (prices["close"] <= 0).sum()

        if invalid > 0:
            validation_errors.append({
                "Rule": "DQ-08",
                "Severity": "CRITICAL",
                "Message": f"{invalid} Invalid Closing Prices"
            })

    # -------------------------
    # DQ-09 Invalid Dates
    # -------------------------
    if "date" in prices.columns:

        invalid_dates = pd.to_datetime(
            prices["date"],
            errors="coerce"
        ).isna().sum()

        if invalid_dates > 0:
            validation_errors.append({
                "Rule": "DQ-09",
                "Severity": "WARNING",
                "Message": f"{invalid_dates} Invalid Dates"
            })

    # -------------------------
    # DQ-10 Invalid Company IDs
    # -------------------------
    if "company_id" in prices.columns and "company_id" in sectors.columns:

        invalid = ~prices["company_id"].isin(sectors["company_id"])

        if invalid.sum() > 0:
            validation_errors.append({
                "Rule": "DQ-10",
                "Severity": "WARNING",
                "Message": f"{invalid.sum()} Invalid Company IDs"
            })

    # -------------------------
    # Create Report
    # -------------------------

    if len(validation_errors) == 0:

        report = pd.DataFrame([{
            "Rule": "-",
            "Severity": "INFO",
            "Message": "No validation failures found."
        }])

    else:

        report = pd.DataFrame(validation_errors)

    report.to_csv(
        OUTPUT_FOLDER / "validation_failures.csv",
        index=False
    )

    print(report)
    print("\nValidation Completed")

    return report


if __name__ == "__main__":
    validate_data()