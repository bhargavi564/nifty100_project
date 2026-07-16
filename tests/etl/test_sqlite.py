import unittest
from pathlib import Path

class TestSQLite(unittest.TestCase):

    def test_database_exists(self):

        self.assertTrue(
            Path("data/nifty100.db").exists()
        )

if __name__ == "__main__":
    unittest.main()