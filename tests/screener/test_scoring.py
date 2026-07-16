import unittest
import pandas as pd

from src.screener.scoring import calculate_composite_score


class TestScoring(unittest.TestCase):

    def setUp(self):

        self.df = pd.DataFrame({

            "return_on_equity_pct":[20,15],
            "net_profit_margin_pct":[10,12],
            "operating_profit_margin_pct":[18,20],
            "debt_to_equity":[0.5,1.2],
            "interest_coverage":[6,4],
            "free_cash_flow_cr":[100,150],
            "cash_from_operations_cr":[120,170],
            "revenue_cagr_5yr":[18,20],
            "pat_cagr_5yr":[15,18]

        })

    def test_composite_score_created(self):

        result = calculate_composite_score(self.df)

        self.assertIn(
            "composite_quality_score",
            result.columns
        )

    def test_score_is_numeric(self):

        result = calculate_composite_score(self.df)

        self.assertTrue(

            pd.api.types.is_numeric_dtype(

                result["composite_quality_score"]

            )

        )

    def test_no_null_scores(self):

        result = calculate_composite_score(self.df)

        self.assertEqual(

            result["composite_quality_score"].isnull().sum(),

            0

        )


if __name__ == "__main__":
    unittest.main()