import os
import sys
import unittest
import pandas as pd
from pathlib import Path

# Resolve paths
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "analytics"))

from capital_allocation_report import run_capital_allocation_report, CHANGES_CSV


class TestCapitalAllocationReport(unittest.TestCase):

    def test_pipeline_execution_and_file_generation(self):
        """Verifies the capital allocation report runs and generates the changes CSV."""
        status = run_capital_allocation_report()
        self.assertEqual(status, "Success")
        self.assertTrue(CHANGES_CSV.exists(), "Pattern changes CSV was not created!")

    def test_pattern_changes_format(self):
        """Verifies the structure of the pattern changes CSV."""
        if not CHANGES_CSV.exists():
            run_capital_allocation_report()
            
        df = pd.read_csv(CHANGES_CSV)
        expected_cols = ["company_id", "prev_year", "prev_pattern", "latest_year", "latest_pattern"]
        for col in expected_cols:
            self.assertIn(col, df.columns)


if __name__ == "__main__":
    unittest.main()
    