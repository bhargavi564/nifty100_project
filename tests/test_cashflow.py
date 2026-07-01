import unittest

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality,
    quality_label,
    capex_intensity,
    capex_label,
    fcf_conversion,
    sign,
    capital_pattern
)


class TestCashFlowKPIs(unittest.TestCase):

    # ----------------------------
    # Free Cash Flow
    # ----------------------------
    def test_free_cash_flow(self):
        self.assertEqual(free_cash_flow(500, -200), 300)

    def test_negative_fcf(self):
        self.assertEqual(free_cash_flow(100, -300), -200)

    # ----------------------------
    # CFO Quality
    # ----------------------------
    def test_cfo_quality(self):
        self.assertEqual(cfo_quality(500, 250), 2.0)

    def test_cfo_quality_zero_pat(self):
        self.assertIsNone(cfo_quality(500, 0))

    # ----------------------------
    # Quality Label
    # ----------------------------
    def test_quality_high(self):
        self.assertEqual(quality_label(1.5), "High Quality")

    def test_quality_moderate(self):
        self.assertEqual(quality_label(0.8), "Moderate")

    def test_quality_low(self):
        self.assertEqual(quality_label(0.3), "Accrual Risk")

    # ----------------------------
    # CapEx Intensity
    # ----------------------------
    def test_capex_intensity(self):
        self.assertEqual(capex_intensity(-50, 1000), 5)

    def test_capex_sales_zero(self):
        self.assertIsNone(capex_intensity(-100, 0))

    # ----------------------------
    # CapEx Label
    # ----------------------------
    def test_capex_asset_light(self):
        self.assertEqual(capex_label(2), "Asset Light")

    def test_capex_moderate(self):
        self.assertEqual(capex_label(5), "Moderate")

    def test_capex_capital_intensive(self):
        self.assertEqual(capex_label(12), "Capital Intensive")

    # ----------------------------
    # FCF Conversion
    # ----------------------------
    def test_fcf_conversion(self):
        self.assertEqual(fcf_conversion(300, 600), 50)

    def test_fcf_conversion_zero_op(self):
        self.assertIsNone(fcf_conversion(300, 0))

    # ----------------------------
    # Sign Function
    # ----------------------------
    def test_positive_sign(self):
        self.assertEqual(sign(10), "+")

    def test_negative_sign(self):
        self.assertEqual(sign(-5), "-")

    # ----------------------------
    # Capital Allocation Pattern
    # ----------------------------
    def test_reinvestor(self):
        self.assertEqual(
            capital_pattern(100, -200, -50),
            "Reinvestor"
        )

    def test_cash_accumulator(self):
        self.assertEqual(
            capital_pattern(100, 50, 25),
            "Cash Accumulator"
        )

    def test_growth_debt(self):
        self.assertEqual(
            capital_pattern(-100, -50, 20),
            "Growth Funded by Debt"
        )

    def test_distress_signal(self):
        self.assertEqual(
            capital_pattern(-50, 100, 20),
            "Distress Signal"
        )


if __name__ == "__main__":
    unittest.main()