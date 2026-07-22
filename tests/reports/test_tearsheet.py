import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "reports"))

from tearsheet import generate_tearsheet, OUTPUT_DIR

class TestPDFTearsheet(unittest.TestCase):

    def test_tearsheet_generation(self):
        """Verifies that the Platypus PDF generator compiles cleanly for a test ticker."""
        test_ticker = "INFY"
        success = generate_tearsheet(test_ticker)
        
        self.assertTrue(success, "PDF Generation function failed.")
        
        expected_pdf = OUTPUT_DIR / f"{test_ticker}_Tearsheet.pdf"
        self.assertTrue(expected_pdf.exists(), f"PDF was not written to disk at {expected_pdf}")
        self.assertGreater(expected_pdf.stat().st_size, 0, "Generated PDF file is empty.")

if __name__ == "__main__":
    unittest.main()