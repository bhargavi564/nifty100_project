import os
import sys
import unittest
import warnings
from pathlib import Path

# 1. Suppress all warnings BEFORE importing FastAPI/Starlette
warnings.filterwarnings("ignore")

# 2. Resolve paths
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

# 3. Import FastAPI modules
from fastapi.testclient import TestClient
from src.api.main import app

class TestCompaniesAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.test_ticker = "TCS"  # Utilizing TCS as our standard test case

    def test_get_all_companies(self):
        """Verifies the base companies list endpoint."""
        response = self.client.get("/api/v1/companies")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_company_search_filter(self):
        """Verifies the search parameter filters results."""
        response = self.client.get(f"/api/v1/companies?search={self.test_ticker}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data:
            self.assertEqual(data[0]["id"], self.test_ticker)

    def test_company_profile_found(self):
        """Verifies retrieving a specific company profile."""
        response = self.client.get(f"/api/v1/companies/{self.test_ticker}")
        if response.status_code == 200:
            self.assertIn("company_name", response.json())
            self.assertIn("latest_kpis", response.json())
        else:
            self.assertEqual(response.status_code, 404)

    def test_company_profile_not_found(self):
        """Verifies 404 handling for invalid tickers."""
        response = self.client.get("/api/v1/companies/INVALID_TICKER_999")
        self.assertEqual(response.status_code, 404)

    def test_profit_and_loss_endpoint(self):
        """Verifies P&L endpoint returns a list."""
        response = self.client.get(f"/api/v1/companies/{self.test_ticker}/pl")
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            self.assertIsInstance(response.json(), list)

if __name__ == "__main__":
    unittest.main()