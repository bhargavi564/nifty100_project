import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "dashboard"))

from qa_integration import run_integration_qa_audit


class TestDay27IntegrationQA(unittest.TestCase):

    def test_integration_qa_pipeline_passes(self):
        """Ensures all stress tests, NaN formatters, and load time targets pass."""
        success = run_integration_qa_audit()
        self.assertTrue(success, "Integration QA audit failed!")


if __name__ == "__main__":
    unittest.main()