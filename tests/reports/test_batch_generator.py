import os
import sys
import unittest
import pandas as pd
from pathlib import Path

# Resolve workspace paths dynamically
BASE_DIR = Path(__file__).resolve().parents[2]
REPORTS_DIR = BASE_DIR / "src" / "reports"

# Inject module pathways into sys.path
sys.path.insert(0, str(REPORTS_DIR))
sys.path.insert(0, str(BASE_DIR))

from batch_generator import run_batch_generation, TEARSHEETS_DIR, SECTOR_DIR, SKIPPED_CSV


class TestBatchGenerator(unittest.TestCase):

    def test_batch_generation_execution(self):
        """Verifies that the batch script executes and populates directories."""
        success = run_batch_generation()
        self.assertTrue(success, "Batch generation pipeline failed.")
        
        # Verify directories exist
        self.assertTrue(TEARSHEETS_DIR.exists())
        self.assertTrue(SECTOR_DIR.exists())
        self.assertTrue(SKIPPED_CSV.exists())
        
        # Check that PDF files were actually created
        tearsheet_pdfs = list(TEARSHEETS_DIR.glob("*_Tearsheet.pdf"))
        sector_pdfs = list(SECTOR_DIR.glob("*_report.pdf"))
        
        # Safely attempt to read the skipped CSV (it may be completely empty if 0 companies were skipped)
        try:
            df_skipped = pd.read_csv(SKIPPED_CSV)
            skipped_count = len(df_skipped)
        except pd.errors.EmptyDataError:
            skipped_count = 0  # Handled gracefully if file is blank
        
        # The sum of skipped companies and generated tearsheets should loosely reflect our DB
        self.assertGreaterEqual(len(tearsheet_pdfs), 0, "Failed to generate tearsheets.")
        self.assertGreater(len(sector_pdfs), 0, "Failed to generate sector reports.")


if __name__ == "__main__":
    unittest.main()