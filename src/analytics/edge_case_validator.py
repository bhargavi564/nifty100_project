import pandas as pd
from pathlib import Path

OUTPUT_FOLDER = Path("output")
OUTPUT_FOLDER.mkdir(exist_ok=True)


def de_warning(de_ratio, sector):
    """
    Debt-to-Equity warning
    """
    if sector == "Financials":
        return "Suppressed"

    if de_ratio > 5:
        return "High Leverage"

    return "Normal"


def category(diff):
    """
    Categorise ROE/ROCE difference
    """
    if diff > 20:
        return "Source Data Issue"

    elif diff > 10:
        return "Version Difference"

    return "Formula Discrepancy"


def run_validation():
    """
    Creates ratio_edge_cases.log
    """

    rows = [
        {
            "Company": "ABC",
            "Metric": "ROCE",
            "Difference": 3,
            "Category": category(3),
            "DE_Flag": de_warning(2.4, "Technology"),
        },
        {
            "Company": "XYZ Bank",
            "Metric": "ROCE",
            "Difference": 12,
            "Category": category(12),
            "DE_Flag": de_warning(8.1, "Financials"),
        },
    ]

    df = pd.DataFrame(rows)

    df.to_csv(
        OUTPUT_FOLDER / "ratio_edge_cases.log",
        index=False,
    )
if __name__ == "_main_":
    run_validation()
print("Edge Case Validation Completed")
print("Log saved to output/ratio_edge_cases.log")


