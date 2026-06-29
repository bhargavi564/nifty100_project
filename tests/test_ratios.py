import unittest

from src.analytics.ratios import *

class TestRatios(unittest.TestCase):

    def test_npm(self):
        self.assertEqual(net_profit_margin(200,1000),20)

    def test_npm_zero_sales(self):
        self.assertEqual(net_profit_margin(200,0),None)

    def test_opm(self):
        self.assertEqual(operating_profit_margin(100,1000),10)

    def test_roe(self):
        self.assertAlmostEqual(roe(250,1000,500),16.67,places=2)

    def test_roe_negative(self):
        self.assertEqual(roe(100,-100,-100),None)

    def test_roce(self):
        self.assertAlmostEqual(roce(400,1000,200,300),26.67,places=2)

    def test_roa(self):
        self.assertEqual(roa(500,5000),10)

    def test_roa_zero(self):
        self.assertEqual(roa(500,0),None)

if __name__=="__main__":
    unittest.main()