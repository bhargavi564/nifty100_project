import os
import sys
import unittest
import pandas as pd
from pathlib import Path

# Resolve workspace paths dynamically
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "src" / "analytics"))

from clustering import run_kmeans_clustering, ELBOW_PLOT, OUTPUT_CSV


class TestKMeansClustering(unittest.TestCase):

    def test_clustering_execution_and_files(self):
        """Verifies that the KMeans script executes, fits clusters, and saves the image and CSV."""
        status = run_kmeans_clustering()
        self.assertEqual(status, "Success", "Clustering pipeline failed.")
        
        # Verify elbow plot exists
        self.assertTrue(ELBOW_PLOT.exists(), f"Elbow plot missing at: {ELBOW_PLOT}")
        self.assertGreater(ELBOW_PLOT.stat().st_size, 0, "Elbow plot file is empty.")
        
        # Verify CSV output
        self.assertTrue(OUTPUT_CSV.exists(), f"Cluster output CSV missing at: {OUTPUT_CSV}")
        
        df = pd.read_csv(OUTPUT_CSV)
        expected_cols = ["company_id", "cluster_id", "cluster_name", "distance_from_centroid"]
        for col in expected_cols:
            self.assertIn(col, df.columns)
            
        # Verify cluster_id range (0-4)
        self.assertTrue(df["cluster_id"].min() >= 0)
        self.assertTrue(df["cluster_id"].max() <= 4)


if __name__ == "__main__":
    unittest.main()