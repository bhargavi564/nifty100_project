import os
import sys
import unittest
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "nlp"))

from parser import parse_analysis_text, OUTPUT_PARSED_CSV, OUTPUT_FAILURES_CSV, REGEX_PATTERN


class TestNLPParser(unittest.TestCase):

    def test_regex_pattern_matching(self):
        """Verifies regex pattern accurately extracts periods and percentages."""
        sample_text = "10 Years: 21% | 5 Years: 15.5%"
        matches = REGEX_PATTERN.findall(sample_text)
        
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0], ("10", "21"))
        self.assertEqual(matches[1], ("5", "15.5"))

    def test_pipeline_execution(self):
        """Verifies main parsing function constructs required output CSV files."""
        status = parse_analysis_text()
        self.assertEqual(status, "Success")
        
        self.assertTrue(OUTPUT_PARSED_CSV.exists())
        self.assertTrue(OUTPUT_FAILURES_CSV.exists())
        
        df_parsed = pd.read_csv(OUTPUT_PARSED_CSV)
        expected_cols = ["company_id", "metric_type", "period_years", "value_pct"]
        for col in expected_cols:
            self.assertIn(col, df_parsed.columns)


if __name__ == "__main__":
    unittest.main()