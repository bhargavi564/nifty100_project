import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


class TestDay24InterfaceComponents(unittest.TestCase):

    def test_screener_script_compiles(self):
        """Validates pages/03_screener.py is syntax error free."""
        scr_path = BASE_DIR / "pages" / "03_screener.py"
        self.assertTrue(scr_path.exists())
        with open(scr_path, "r", encoding="utf-8") as f:
            self.assertIsNotNone(compile(f.read(), str(scr_path), "exec"))

    def test_peer_script_compiles(self):
        """Validates pages/04_peers.py is syntax error free."""
        peer_path = BASE_DIR / "pages" / "04_peers.py"
        self.assertTrue(peer_path.exists())
        with open(peer_path, "r", encoding="utf-8") as f:
            self.assertIsNotNone(compile(f.read(), str(peer_path), "exec"))


if __name__ == "__main__":
    unittest.main()