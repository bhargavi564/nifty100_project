import unittest
from pathlib import Path

class TestLoader(unittest.TestCase):

    def test_raw_folder_exists(self):
        self.assertTrue(Path("data/raw").exists())

    def test_processed_folder_exists(self):
        self.assertTrue(Path("data/processed").exists())

    def test_companies_file_exists(self):
        self.assertTrue(Path("data/raw/companies.xlsx").exists())

if __name__ == "__main__":
    unittest.main()