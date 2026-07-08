import unittest
import sys
from pathlib import Path
import pandas as pd

# Add src/screener to Python path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src" / "screener"))

from presets import (
    quality_compounder,
    value_pick,
    growth_accelerator,
    dividend_champion,
    debt_free_bluechip,
    turnaround_watch,
)


class TestPresets(unittest.TestCase):

    def test_quality_compounder(self):
        df = quality_compounder()
        self.assertIsInstance(df, pd.DataFrame)

    def test_value_pick(self):
        df = value_pick()
        self.assertIsInstance(df, pd.DataFrame)

    def test_growth_accelerator(self):
        df = growth_accelerator()
        self.assertIsInstance(df, pd.DataFrame)

    def test_dividend_champion(self):
        df = dividend_champion()
        self.assertIsInstance(df, pd.DataFrame)

    def test_debt_free_bluechip(self):
        df = debt_free_bluechip()
        self.assertIsInstance(df, pd.DataFrame)

    def test_turnaround_watch(self):
        df = turnaround_watch()
        self.assertIsInstance(df, pd.DataFrame)


if __name__ == "__main__":
    unittest.main()