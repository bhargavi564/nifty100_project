import os
import sys
import unittest
import pandas as pd
from pathlib import Path

# Resolve workspace paths dynamically
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "analytics"))

from cluster_profiling import (
    run_cluster_profiling_and_stats, 
    HEATMAP_PLOT, 
    OUTLIER_CSV, 
    STATS_CSV
)


class TestClusterProfiling(unittest.TestCase):

    def test_profiling_and_stats_execution(self):
        """Verifies that the script generates the heatmap and output CSVs."""
        status = run_cluster_profiling_and_stats()
        self.assertEqual(status, "Success", "Cluster profiling pipeline failed.")
        
        # Verify heatmap exists
        self.assertTrue(HEATMAP_PLOT.exists(), "Correlation heatmap is missing!")
        
        # Verify Outlier CSV exists
        self.assertTrue(OUTLIER_CSV.exists(), "Outlier report CSV is missing!")
        
        # Verify Portfolio Stats CSV exists
        self.assertTrue(STATS_CSV.exists(), "Portfolio stats CSV is missing!")
        
        # Check Portfolio Stats columns
        df_stats = pd.read_csv(STATS_CSV)
        expected_cols = ["KPI", "P10", "P25", "P50", "P75", "P90", "Mean", "Std"]
        for col in expected_cols:
            self.assertIn(col, df_stats.columns)


if __name__ == "__main__":
    unittest.main()