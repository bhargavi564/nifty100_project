import pandas as pd


def normalize(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series([50] * len(series), index=series.index)

    return ((series - minimum) / (maximum - minimum)) * 100


def get_score(df, column, reverse=False):
    """
    Safely returns normalized score.
    If column doesn't exist, returns zeros.
    """

    if column not in df.columns:
        return pd.Series([0] * len(df), index=df.index)

    values = pd.to_numeric(df[column], errors="coerce").fillna(0)

    score = normalize(values)

    if reverse:
        score = 100 - score

    return score


def calculate_composite_score(df):

    # -----------------------------
    # Profitability
    # -----------------------------

    df["roe_score"] = get_score(df, "return_on_equity_pct")

    df["roce_score"] = get_score(df, "roce")

    df["npm_score"] = get_score(df, "net_profit_margin_pct")

    df["profitability_score"] = (
        df["roe_score"] * 0.15
        + df["roce_score"] * 0.10
        + df["npm_score"] * 0.10
    )

    # -----------------------------
    # Cash Quality
    # -----------------------------

    df["fcf_score"] = get_score(df, "fcf_conversion_rate")

    df["cfo_score"] = get_score(df, "cfo_quality_score")

    if "free_cash_flow_cr" in df.columns:
        fcf = pd.to_numeric(
            df["free_cash_flow_cr"],
            errors="coerce"
        ).fillna(0)

        df["fcf_positive_score"] = (fcf > 0).astype(int) * 100

    else:
        df["fcf_positive_score"] = 0

    df["cash_quality_score"] = (
        df["fcf_score"] * 0.15
        + df["cfo_score"] * 0.10
        + df["fcf_positive_score"] * 0.05
    )

    # -----------------------------
    # Growth
    # -----------------------------

    df["revenue_score"] = get_score(df, "revenue_cagr_5yr")

    df["pat_score"] = get_score(df, "pat_cagr_5yr")

    df["growth_score"] = (
        df["revenue_score"] * 0.10
        + df["pat_score"] * 0.10
    )

    # -----------------------------
    # Leverage
    # -----------------------------

    df["de_score"] = get_score(
        df,
        "debt_to_equity",
        reverse=True
    )

    df["icr_score"] = get_score(
        df,
        "interest_coverage"
    )

    df["leverage_score"] = (
        df["de_score"] * 0.10
        + df["icr_score"] * 0.05
    )

    # -----------------------------
    # Final Composite Score
    # -----------------------------

    df["composite_quality_score"] = (
        df["profitability_score"]
        + df["cash_quality_score"]
        + df["growth_score"]
        + df["leverage_score"]
    )

    return df


if __name__ == "__main__":

    df = pd.read_csv(
        "data/processed/financial_ratios.csv"
    )

    df = calculate_composite_score(df)

    df.to_csv(
        "output/financial_ratios_scored.csv",
        index=False
    )

    print("\nComposite Score Generated Successfully")

    print(df[[
        "company_id",
        "year",
        "composite_quality_score"
    ]].head())