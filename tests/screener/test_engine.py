import unittest
import pandas as pd

from src.screener.engine import apply_filters


class TestFilterEngine(unittest.TestCase):

    def setUp(self):

        self.df = pd.DataFrame({

            "company_id": ["A", "B", "C"],

            "return_on_equity_pct": [20, 10, 30],

            "debt_to_equity": [0.5, 2.0, 0.8],

            "free_cash_flow": [500, -100, 800],

            "revenue_cagr_5yr": [12, 5, 18],

            "pat_cagr_5yr": [15, 2, 20],

            "operating_profit_margin_pct": [18, 8, 25],

            "interest_coverage": [5, 1, 10],

            "market_cap": [15000, 5000, 25000],

            "net_profit": [800, 50, 1200],

            "eps_cagr_5yr": [14, 3, 18],

            "asset_turnover": [1.2, 0.5, 1.8],

            "sales": [1000, 200, 3000],

            "composite_quality_score": [90, 40, 95],

            "broad_sector": ["IT", "Financials", "Auto"],

            "icr_label": ["Normal", "Debt Free", "Normal"]

        })

        self.config = {

            "roe_min": 15,

            "debt_to_equity_max": 1,

            "fcf_min": 0,

            "revenue_cagr_5yr_min": 10,

            "pat_cagr_5yr_min": 10,

            "opm_min": 15,

            "icr_min": 2,

            "market_cap_min": 10000,

            "net_profit_min": 100,

            "eps_cagr_min": 10,

            "asset_turnover_min": 1,

            "sales_min": 500

        }

    def test_roe_filter(self):

        result = apply_filters(self.df.copy(), self.config)

        self.assertTrue(
            (result["return_on_equity_pct"] >= 15).all()
        )

    def test_de_filter(self):

        result = apply_filters(self.df.copy(), self.config)

        self.assertTrue(
            (result["debt_to_equity"] <= 1).all()
        )

    def test_fcf_filter(self):

        result = apply_filters(self.df.copy(), self.config)

        self.assertTrue(
            (result["free_cash_flow"] >= 0).all()
        )

    def test_market_cap_filter(self):

        result = apply_filters(self.df.copy(), self.config)

        self.assertTrue(
            (result["market_cap"] >= 10000).all()
        )

    def test_sales_filter(self):

        result = apply_filters(self.df.copy(), self.config)

        self.assertTrue(
            (result["sales"] >= 500).all()
        )

    def test_sorting(self):

        result = apply_filters(self.df.copy(), self.config)

        scores = result["composite_quality_score"].tolist()

        self.assertEqual(
            scores,
            sorted(scores, reverse=True)
        )


if __name__ == "__main__":
    unittest.main()