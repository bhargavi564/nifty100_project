import pandas as pd


def normalize_columns(df):
    """
    Standardize column names.
    """
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def clean_dataframe(df):
    """
    Clean the dataframe.
    """
    df = normalize_columns(df)

    df.drop_duplicates(inplace=True)
    df.dropna(how="all", inplace=True)
    df.fillna("", inplace=True)

    return df


if __name__ == "__main__":

    sample = pd.DataFrame({
        " Company Name ": ["TCS", "Infosys", "Infosys"],
        " Market Cap ": [1000, 2000, 2000],
        " Sector ": ["IT", "IT", "IT"]
    })

    print("Before Cleaning:\n")
    print(sample)

    cleaned = clean_dataframe(sample)

    print("\nAfter Cleaning:\n")
    print(cleaned)