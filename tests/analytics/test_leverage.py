import unittest

from src.analytics.leverage import *

class TestLeverage(unittest.TestCase):

    def test_de_ratio(self):
        self.assertEqual(debt_to_equity(100,200,300),0.2)

    def test_debt_free(self):
        self.assertEqual(debt_to_equity(0,200,300),0)

    def test_high_flag(self):
        self.assertTrue(high_leverage_flag(6,"IT"))

    def test_financial_sector(self):
        self.assertFalse(high_leverage_flag(6,"Financials"))

    def test_icr(self):
        self.assertEqual(interest_coverage(100,20,20),6)

    def test_icr_none(self):
        self.assertEqual(interest_coverage(100,20,0),None)

    def test_label(self):
        self.assertEqual(icr_label(None),"Debt Free")

    def test_asset_turnover(self):
        self.assertEqual(asset_turnover(1000,500),2)

if __name__=="__main__":
    unittest.main()