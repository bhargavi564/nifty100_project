import os
import sys
import unittest
import pandas as pd

# 1. Resolve workspace paths dynamically
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCREENER_DIR = os.path.join(BASE_DIR, "src", "screener")

sys.path.insert(0, SCREENER_DIR)
sys.path.insert(0, BASE_DIR)

# 2. Safe import of the screener strategies
from presets import (
    quality_compounder,
    value_pick,
    growth_accelerator,
    dividend_champion,
    debt_free_bluechip,
    turnaround_watch,
)


class TestScreenerPresets(unittest.TestCase):

    def setUp(self):
        """Set up a clean mock DataFrame before every test run."""
        self.df = pd.DataFrame({
            "ticker": ["A", "B", "C", "D"],
            "return_on_equity_pct": [20.0, 10.0, 18.0, 15.0],
            "debt_to_equity": [0.2, 1.5, 0.0, 0.5],
            "free_cash_flow_cr": [100.0, -50.0, 200.0, 10.0],
            "revenue_cagr_5yr": [12.0, 8.0, 16.0, 9.0],  # Changed C from 15.0 to 16.0
            "price_to_earnings": [15.0, 25.0, 12.0, 18.0],
            "price_to_book": [2.0, 4.0, 1.5, 2.8],
            "dividend_yield_pct": [1.5, 0.5, 3.0, 2.5],
            "dividend_payout_ratio_pct": [40.0, 90.0, 50.0, 70.0],
            "pat_cagr_5yr": [25.0, 10.0, 30.0, 15.0],
            "revenue_cr": [6000, 1200, 8000, 3000],
            "composite_quality_score": [80, 50, 95, 70]
        })

    def test_quality_compounder(self):
        """Must match: ROE > 15, D/E < 1, FCF > 0, 5Yr Rev CAGR > 10."""
        result = quality_compounder(self.df)
        self.assertEqual(list(result["ticker"]), ["C", "A"])

    def test_value_pick(self):
        """Must match: P/E < 20, P/B < 3, D/E < 2, Dividend Yield > 1."""
        result = value_pick(self.df)
        self.assertEqual(list(result["ticker"]), ["C", "A", "D"])

    def test_growth_accelerator(self):
        """Must match: PAT CAGR > 20, Rev CAGR > 15, D/E < 2."""
        result = growth_accelerator(self.df)
        self.assertEqual(list(result["ticker"]), ["C"])

    def test_dividend_champion(self):
        """Must match: Div Yield > 2, Payout Ratio < 80, FCF > 0."""
        result = dividend_champion(self.df)
        self.assertEqual(list(result["ticker"]), ["C", "D"])

    def test_debt_free_bluechip(self):
        """Must match: D/E == 0, ROE > 12, Revenue > 5000."""
        result = debt_free_bluechip(self.df)
        self.assertEqual(list(result["ticker"]), ["C"])

    def test_turnaround_watch_with_no_change_col(self):
        """Verifies that empty DataFrames are handled gracefully without errors."""
        empty_df = pd.DataFrame()
        result = turnaround_watch(empty_df)
        self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main()