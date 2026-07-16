import os
import sys
import unittest
from unittest.mock import patch

# 1. Step back exactly 2 directories from tests/etl/ to get to 'sprint1'
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 2. Point directly to 'sprint1/src/etl' where run_pipeline.py and loader.py live
ETL_DIR = os.path.join(BASE_DIR, "src", "etl")

# 3. Insert both paths into sys.path
sys.path.insert(0, ETL_DIR)
sys.path.insert(0, BASE_DIR)

# 4. Import the main function from run_pipeline
from run_pipeline import main


class TestRunPipeline(unittest.TestCase):

    @patch("run_pipeline.load_database")
    @patch("run_pipeline.validate_data")
    @patch("run_pipeline.load_all_files")
    def test_pipeline_success(
        self, mock_load_files, mock_validate, mock_load_db
    ):
        """Test that the pipeline runs sequentially without any arguments."""

        # Act
        with patch("sys.stdout"):
            main()

        # Assert: Verify each function was called sequentially
        mock_load_files.assert_called_once()
        mock_validate.assert_called_once()
        mock_load_db.assert_called_once()

    @patch("run_pipeline.load_all_files")
    @patch("sys.exit")
    def test_pipeline_failure_during_extraction(self, mock_exit, mock_load_files):
        """Test that if Step 1 fails, the pipeline aborts gracefully."""

        # Arrange
        mock_load_files.side_effect = Exception("File missing or corrupted")

        # Act
        with patch("sys.stdout"):
            main()

        # Assert
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()