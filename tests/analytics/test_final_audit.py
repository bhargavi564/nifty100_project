import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "analytics"))

from final_audit import run_exit_criteria_audit


class TestFinalDeliverables(unittest.TestCase):

    def test_all_deliverables_and_exit_criteria(self):
        """Validates that all exit criteria and deliverables pass."""
        success = run_exit_criteria_audit()
        self.assertTrue(success, "final exit criteria check failed!")


if __name__ == "__main__":
    unittest.main()