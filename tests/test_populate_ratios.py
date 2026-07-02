import unittest
import sqlite3
import pandas as pd


class TestPopulateRatios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect("data/nifty100.db")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # Test 1
    def test_table_exists(self):

        query = """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='financial_ratios'
        """

        result = pd.read_sql(query, self.conn)

        self.assertEqual(len(result), 1)

    # Test 2
    def test_row_count(self):

        df = pd.read_sql(
            "SELECT COUNT(*) AS total FROM financial_ratios",
            self.conn
        )

        self.assertGreater(df["total"][0], 0)

    # Test 3
    def test_company_id_column(self):

        df = pd.read_sql(
            "SELECT company_id FROM financial_ratios LIMIT 5",
            self.conn
        )

        self.assertIn("company_id", df.columns)

    # Test 4
    def test_year_column(self):

        df = pd.read_sql(
            "SELECT year FROM financial_ratios LIMIT 5",
            self.conn
        )

        self.assertIn("year", df.columns)

    # Test 5
    def test_net_profit_margin_column(self):

        df = pd.read_sql(
            "SELECT net_profit_margin_pct FROM financial_ratios LIMIT 5",
            self.conn
        )

        self.assertIn("net_profit_margin_pct", df.columns)

    # Test 6
    def test_roe_column(self):

        df = pd.read_sql(
            "SELECT return_on_equity_pct FROM financial_ratios LIMIT 5",
            self.conn
        )

        self.assertIn("return_on_equity_pct", df.columns)

    # Test 7
    def test_debt_equity_column(self):

        df = pd.read_sql(
            "SELECT debt_to_equity FROM financial_ratios LIMIT 5",
            self.conn
        )

        self.assertIn("debt_to_equity", df.columns)

    # Test 8
    def test_composite_score(self):

        df = pd.read_sql(
            "SELECT composite_quality_score FROM financial_ratios LIMIT 5",
            self.conn
        )

        self.assertIn("composite_quality_score", df.columns)

    # Test 9
    def test_no_duplicate_company_year(self):

        query = """
        SELECT company_id,
               year,
               COUNT(*) cnt
        FROM financial_ratios
        GROUP BY company_id, year
        HAVING COUNT(*) > 1
        """

        df = pd.read_sql(query, self.conn)

        self.assertEqual(len(df), 0)

    # Test 10
    def test_no_null_company(self):

        df = pd.read_sql(
            """
            SELECT *
            FROM financial_ratios
            WHERE company_id IS NULL
            """,
            self.conn
        )

        self.assertEqual(len(df), 0)


if __name__ == "__main__":
    unittest.main()