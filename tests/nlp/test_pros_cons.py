import os
import sys
import unittest
import pandas as pd
from pathlib import Path

# 1. Resolve workspace paths dynamically
BASE_DIR = Path(__file__).resolve().parents[2]
NLP_DIR = BASE_DIR / "src" / "nlp"

# Inject module pathways into sys.path
sys.path.insert(0, str(NLP_DIR))
sys.path.insert(0, str(BASE_DIR))

# 2. Import generator function and output path
from pros_cons_generator import generate_pros_and_cons, OUTPUT_CSV


class TestProsConsGenerator(unittest.TestCase):

    def test_generator_execution(self):
        """Verifies generator runs cleanly and creates valid CSV output."""
        status = generate_pros_and_cons()
        self.assertEqual(status, "Success")
        self.assertTrue(OUTPUT_CSV.exists(), f"Output file missing at: {OUTPUT_CSV}")

    def test_every_company_has_pro_and_con(self):
        """Exit Criteria Check: Ensures every company in the output has at least 1 pro and 1 con."""
        # Ensure file exists before running assertions
        if not OUTPUT_CSV.exists():
            generate_pros_and_cons()

        df = pd.read_csv(OUTPUT_CSV)
        companies = df["company_id"].unique()

        self.assertGreater(len(companies), 0, "No companies found in output!")

        for comp in companies:
            comp_df = df[df["company_id"] == comp]
            has_pro = (comp_df["type"] == "pro").any()
            has_con = (comp_df["type"] == "con").any()

            self.assertTrue(has_pro, f"Company {comp} is missing a Pro entry!")
            self.assertTrue(has_con, f"Company {comp} is missing a Con entry!")

    def test_confidence_threshold(self):
        """Verifies all output rows have a confidence score > 60%."""
        if not OUTPUT_CSV.exists():
            generate_pros_and_cons()

        df = pd.read_csv(OUTPUT_CSV)
        self.assertTrue(
            (df["confidence_pct"] > 60).all(),
            "Found entries with confidence <= 60%!"
        )


if __name__ == "__main__":
    unittest.main()