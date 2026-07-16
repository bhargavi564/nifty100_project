import os
import sys
import unittest
import sqlite3
import pandas as pd
from unittest.mock import patch, MagicMock

# 1. Resolve workspace paths dynamically
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ANALYTICS_DIR = os.path.join(BASE_DIR, "src", "analytics")

sys.path.insert(0, ANALYTICS_DIR)
sys.path.insert(0, BASE_DIR)

# 2. Import the calculation function
from peer import compute_peer_percentiles


class NoCloseConnection:
    """A proxy wrapper around sqlite3.Connection that blocks the .close() method

    from terminating our in-memory test database, allowing verification assertions.
    """
    def __init__(self, real_conn):
        self._conn = real_conn

    def cursor(self):
        return self._conn.cursor()

    def commit(self):
        return self._conn.commit()

    def close(self):
        # Intercept and ignore the close call to keep database alive for assertion queries
        pass

    def __getattr__(self, item):
        # Forward any other call (like execute, rollback, etc.) to the real connection
        return getattr(self._conn, item)


class TestPeerAnalytics(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory SQLite database and test records."""
        self.real_conn = sqlite3.connect(":memory:")
        self.cursor = self.real_conn.cursor()

        # Create raw metrics table
        self.cursor.execute("""
            CREATE TABLE company_metrics (
                company_id TEXT,
                metric TEXT,
                value REAL,
                year INTEGER
            )
        """)

        metrics_data = [
            # IT Services Group (TCS, INFY)
            ("TCS", "ROE", 40.0, 2026),
            ("TCS", "D/E", 0.1, 2026),
            ("INFY", "ROE", 30.0, 2026),
            ("INFY", "D/E", 0.0, 2026),
            # Banking Group (HDFCBANK, SBIN)
            ("HDFCBANK", "ROE", 15.0, 2026),
            ("HDFCBANK", "D/E", 1.0, 2026),
            ("SBIN", "ROE", 10.0, 2026),
            ("SBIN", "D/E", 1.5, 2026),
        ]
        self.cursor.executemany(
            "INSERT INTO company_metrics VALUES (?, ?, ?, ?)", metrics_data
        )
        self.real_conn.commit()

        # Mock peer mapping dataframe
        self.mock_peer_df = pd.DataFrame({
            "company_id": ["TCS", "INFY", "HDFCBANK", "SBIN"],
            "peer_group_name": ["IT", "IT", "Banking", "Banking"]
        })

    def tearDown(self):
        """Clean up database connections."""
        self.real_conn.close()

    @patch("os.path.exists")
    def test_missing_excel_file_handling(self, mock_exists):
        """Should gracefully stop and return configuration warning when Excel is missing."""
        mock_exists.side_effect = lambda path: "peer_groups.xlsx" not in str(path)

        status = compute_peer_percentiles(db_path="nifty100.db", excel_path="peer_groups.xlsx")
        self.assertEqual(status, "Missing Peer Groups Configuration")

    @patch("pandas.read_excel")
    @patch("os.path.exists")
    def test_missing_database_file_handling(self, mock_exists, mock_read_excel):
        """Should gracefully stop and return database warning when SQLite file is missing."""
        # Force the Excel file to exist, but the Database file to be missing
        mock_exists.side_effect = lambda path: "nifty100.db" not in str(path)
        mock_read_excel.return_value = self.mock_peer_df

        status = compute_peer_percentiles(db_path="nifty100.db", excel_path="peer_groups.xlsx")
        self.assertEqual(status, "Missing SQLite Database")

    @patch("os.path.exists")
    @patch("pandas.read_excel")
    @patch("sqlite3.connect")
    def test_successful_calculation_and_rank_inversion(self, mock_connect, mock_read_excel, mock_exists):
        """Verifies full processing cycle, relative ranks, and inverted D/E values."""
        mock_exists.return_value = True
        mock_read_excel.return_value = self.mock_peer_df
        
        # Intercept database connect call to return our mock wrapper instead
        mock_connect.return_value = NoCloseConnection(self.real_conn)

        # Run calculations
        with patch("warnings.warn"):
            status = compute_peer_percentiles(db_path="dummy.db", excel_path="dummy.xlsx")
        
        self.assertEqual(status, "Calculations completed successfully")

        # Read the newly populated table from our in-memory database
        result_df = pd.read_sql_query("SELECT * FROM peer_percentiles", self.real_conn)

        # Ensure correct columns exist
        expected_cols = {"company_id", "peer_group_name", "metric", "value", "percentile_rank", "year"}
        self.assertTrue(expected_cols.issubset(result_df.columns))

        # Check ROE Percentiles: TCS (40 ROE) vs INFY (30 ROE) -> TCS must have a higher rank
        tcs_roe = result_df[(result_df["company_id"] == "TCS") & (result_df["metric"] == "ROE")].iloc[0]
        infy_roe = result_df[(result_df["company_id"] == "INFY") & (result_df["metric"] == "ROE")].iloc[0]
        self.assertGreater(tcs_roe["percentile_rank"], infy_roe["percentile_rank"])

        # Check Inverse Percentiles (D/E): INFY (0.0 D/E) must have a higher rank than TCS (0.1 D/E)
        tcs_de = result_df[(result_df["company_id"] == "TCS") & (result_df["metric"] == "D/E")].iloc[0]
        infy_de = result_df[(result_df["company_id"] == "INFY") & (result_df["metric"] == "D/E")].iloc[0]
        self.assertGreater(infy_de["percentile_rank"], tcs_de["percentile_rank"])


if __name__ == "__main__":
    unittest.main()