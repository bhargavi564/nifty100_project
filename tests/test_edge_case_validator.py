import unittest

from src.analytics.edge_case_validator import de_warning, category


class TestEdgeCaseValidator(unittest.TestCase):

    def test_financial_sector(self):
        self.assertEqual(
            de_warning(10, "Financials"),
            "Suppressed"
        )

    def test_high_leverage(self):
        self.assertEqual(
            de_warning(8, "Technology"),
            "High Leverage"
        )

    def test_normal(self):
        self.assertEqual(
            de_warning(2, "Technology"),
            "Normal"
        )

    def test_boundary(self):
        self.assertEqual(
            de_warning(5, "Technology"),
            "Normal"
        )

    def test_formula(self):
        self.assertEqual(
            category(3),
            "Formula Discrepancy"
        )

    def test_version(self):
        self.assertEqual(
            category(15),
            "Version Difference"
        )

    def test_source(self):
        self.assertEqual(
            category(25),
            "Source Data Issue"
        )

    def test_boundary10(self):
        self.assertEqual(
            category(10),
            "Formula Discrepancy"
        )

    def test_boundary20(self):
        self.assertEqual(
            category(20),
            "Version Difference"
        )


if __name__ == "__main__":
    unittest.main()