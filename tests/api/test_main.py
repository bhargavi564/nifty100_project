import os
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Resolve paths
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from src.api.main import app

class TestFastAPIServer(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Verifies the /api/v1/health endpoint returns correct structure and 200 OK."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("version", data)
        self.assertIn("uptime_seconds", data)
        self.assertIn("db_row_counts", data)
        
        # Verify db_row_counts is a dictionary (it will contain tables if DB exists)
        self.assertIsInstance(data["db_row_counts"], dict)

if __name__ == "__main__":
    unittest.main()