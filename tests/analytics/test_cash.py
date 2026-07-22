import os
import sys
import unittest
import pandas as pd
from pathlib import Path

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]
ANALYTICS_DIR = BASE_DIR / "src" / "analytics"

sys.path.insert(0, str(ANALYTICS_DIR))
sys.path.insert(0, str(BASE_DIR))

from cashflow import (
    run_cashflow_intelligence_pipeline,
    free_cash_flow,
    capex_intensity,
    capital_pattern,
    OUTPUT_XLSX,
    OUTPUT_CSV
)


class TestCashflowKPIs(unittest.TestCase):

    def test_kpi_helper_functions(self):
        """Verifies mathematical helper formulas."""
        self.assertEqual(free_cash_flow(100, -30), 70)
        self.assertEqual(capex_intensity(-50, 1000), 5.0)
        self.assertEqual(capital_pattern(100, -50, -20), "+/-/-")

    def test_pipeline_execution_and_deliverables(self):
        """Verifies pipeline execution and generated output structures."""
        status = run_cashflow_intelligence_pipeline()
        self.assertEqual(status, "Success")

        self.assertTrue(OUTPUT_XLSX.exists(), "Output Excel file missing!")
        self.assertTrue(OUTPUT_CSV.exists(), "Distress alerts CSV missing!")

        df_out = pd.read_excel(OUTPUT_XLSX)
        expected_cols = [
            "company_id", "sector", "cfo_quality_score", "cfo_quality_label",
            "capex_intensity_pct", "capex_label", "fcf_cagr_5yr",
            "fcf_conversion_pct", "distress_flag", "deleveraging_flag",
            "capital_allocation_label"
        ]
        for col in expected_cols:
            self.assertIn(col, df_out.columns)


if __name__ == "__main__":
    unittest.main()