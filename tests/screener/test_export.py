import unittest
from pathlib import Path
import tempfile
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.screener.export import export_results


class TestExport(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "company_id": ["ABB", "TCS"],
            "year": [2024, 2024],
            "composite_quality_score": [80, 92],
        })

    def test_export_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "test_export.xlsx"
            result = export_results(self.df, output_file)
            self.assertTrue(output_file.exists())
            self.assertTrue(result.endswith(".xlsx"))

    def test_dataframe_not_empty(self):
        self.assertFalse(self.df.empty)

    def test_row_count(self):
        self.assertEqual(len(self.df), 2)


if __name__ == "__main__":
    unittest.main()