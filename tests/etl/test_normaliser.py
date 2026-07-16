import unittest
import pandas as pd
from src.etl.normaliser import normalize_columns

class TestNormaliser(unittest.TestCase):

    def test_column_names(self):

        df = pd.DataFrame({
            " Company Name ": ["ABC"],
            " Market Cap ": [100]
        })

        df = normalize_columns(df)

        self.assertEqual(
            list(df.columns),
            ["company_name", "market_cap"]
        )

if __name__ == "__main__":
    unittest.main()