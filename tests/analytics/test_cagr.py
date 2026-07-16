import unittest

from src.analytics.cagr import (
    calculate_cagr,
    revenue_cagr,
    pat_cagr,
    eps_cagr,
    check_years
)


class TestCAGR(unittest.TestCase):

    # Test 1 - Normal CAGR
    def test_normal_cagr(self):
        value, flag = calculate_cagr(100, 200, 5)
        self.assertEqual(flag, "NORMAL")
        self.assertIsNotNone(value)

    # Test 2 - Zero Base
    def test_zero_base(self):
        value, flag = calculate_cagr(0, 100, 5)
        self.assertEqual(flag, "ZERO_BASE")
        self.assertIsNone(value)

    # Test 3 - Turnaround
    def test_turnaround(self):
        value, flag = calculate_cagr(-20, 40, 5)
        self.assertEqual(flag, "TURNAROUND")
        self.assertIsNone(value)

    # Test 4 - Decline to Loss
    def test_decline_to_loss(self):
        value, flag = calculate_cagr(100, -40, 5)
        self.assertEqual(flag, "DECLINE_TO_LOSS")
        self.assertIsNone(value)

    # Test 5 - Both Negative
    def test_both_negative(self):
        value, flag = calculate_cagr(-100, -20, 5)
        self.assertEqual(flag, "BOTH_NEGATIVE")
        self.assertIsNone(value)

    # Test 6 - Invalid Years
    def test_invalid_years(self):
        value, flag = calculate_cagr(100, 200, 0)
        self.assertEqual(flag, "INVALID")
        self.assertIsNone(value)

    # Test 7 - Insufficient Years
    def test_check_years(self):
        value, flag = check_years(2, 5)
        self.assertEqual(flag, "INSUFFICIENT")

    # Test 8 - Revenue CAGR
    def test_revenue_cagr(self):
        value, flag = revenue_cagr(100, 200, 5)
        self.assertEqual(flag, "NORMAL")

    # Test 9 - PAT CAGR
    def test_pat_cagr(self):
        value, flag = pat_cagr(100, 300, 5)
        self.assertEqual(flag, "NORMAL")

    # Test 10 - EPS CAGR
    def test_eps_cagr(self):
        value, flag = eps_cagr(10, 25, 5)
        self.assertEqual(flag, "NORMAL")


if __name__ == "__main__":
    unittest.main()