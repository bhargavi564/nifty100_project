import unittest
import pandas as pd

class TestValidator(unittest.TestCase):

    def test_company_name_column(self):

        df = pd.DataFrame({
            "company_name":["ABC"]
        })

        self.assertIn(
            "company_name",
            df.columns
        )

if __name__ == "__main__":
    unittest.main()