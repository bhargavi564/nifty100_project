import os
import sys
import unittest
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "analytics"))

from valuation import run_valuation_pipeline, OUTPUT_XLSX, OUTPUT_CSV


class TestValuationModule(unittest.TestCase):

    def setUp(self):
        """Set up dynamic artifact output environment properties."""
        self.mock_db = BASE_DIR / "data" / "nifty100.db"
        self.mock_excel = BASE_DIR / "data" / "market_cap.xlsx"

    def test_pipeline_execution_and_file_generation(self):
        """Verifies valuation script executes to conclusion and constructs correct report structures."""
        status = run_valuation_pipeline(db_path=self.mock_db, excel_path=self.mock_excel)
        self.assertEqual(status, "Success")
        
        # Check files exist
        self.assertTrue(OUTPUT_XLSX.exists(), "Excel report artifact missing!")
        self.assertTrue(OUTPUT_CSV.exists(), "CSV flags report artifact missing!")

        # Verify structured layout properties match criteria
        df_summary = pd.read_excel(OUTPUT_XLSX)
        expected_headers = ["company_id", "company_name", "sector", "P/E", "P/B", "EV/EBITDA", "FCF_yield_pct", "flag"]
        for header in expected_headers:
            self.assertIn(header, df_summary.columns)


if __name__ == "__main__":
    unittest.main()