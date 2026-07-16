import os
import sys
import unittest
import shutil
import sqlite3
import pandas as pd
from pathlib import Path

# Resolve paths
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "analytics"))
sys.path.insert(0, str(BASE_DIR))

from radar import generate_radar_charts


class TestRadarCharts(unittest.TestCase):

    def setUp(self):
        """Set up dynamic mock paths and write dummy test DB data."""
        self.test_dir = BASE_DIR / "tests" / "temp_test_outputs"
        self.test_db = self.test_dir / "test_nifty100.db"
        self.test_dir.mkdir(parents=True, exist_ok=True)

        # Create temporary database
        self.conn = sqlite3.connect(self.test_db)
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE peer_percentiles (
                company_id TEXT,
                peer_group_name TEXT,
                metric TEXT,
                percentile_rank REAL,
                year INTEGER
            )
        """)
        
        # Insert mock metrics for 1 company (8 required metrics)
        metrics = ["ROE", "ROCE", "Net Profit Margin", "D/E", "FCF", "PAT CAGR 5yr", "Revenue CAGR 5yr", "Composite Score"]
        mock_records = [( "TCS", "IT", m, 0.85, 2026 ) for m in metrics]
        cursor.executemany("INSERT INTO peer_percentiles VALUES (?, ?, ?, ?, ?)", mock_records)
        self.conn.commit()
        self.conn.close()

    def tearDown(self):
        """Clean up temporary test directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_chart_generation_creates_png(self):
        """Verify pipeline successfully exports a PNG named {company}_radar.png."""
        status = generate_radar_charts(db_path=self.test_db, output_dir=self.test_dir)
        self.assertEqual(status, "Generation complete")

        expected_file = self.test_dir / "TCS_radar.png"
        self.assertTrue(expected_file.exists(), f"Expected chart export missing at: {expected_file}")


if __name__ == "__main__":
    unittest.main()