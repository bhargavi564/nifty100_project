import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "reports"))

from portfolio_summary import run_portfolio_summary, OUTPUT_PDF

class TestPortfolioSummary(unittest.TestCase):

    def test_portfolio_generation(self):
        """Verifies the portfolio summary PDF generates successfully."""
        success = run_portfolio_summary()
        self.assertTrue(success, "Portfolio PDF generation failed.")
        self.assertTrue(OUTPUT_PDF.exists(), "Portfolio PDF file is missing!")
        self.assertGreater(OUTPUT_PDF.stat().st_size, 1000, "Portfolio PDF is empty!")

if __name__ == "__main__":
    unittest.main()