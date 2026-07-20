import os
import sys
import unittest
from pathlib import Path

# Resolve workspace paths dynamically
BASE_DIR = Path(__file__).resolve().parents[2]


class TestDay25InterfaceScripts(unittest.TestCase):

    def test_trends_page_syntax_and_compilation(self):
        """Validates that pages/05_trends.py is free of syntax errors and compiles cleanly."""
        file_path = BASE_DIR / "pages" / "05_trends.py"
        self.assertTrue(file_path.exists(), f"Missing target page file at: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
            
        try:
            compiled = compile(source_code, str(file_path), "exec")
            self.assertIsNotNone(compiled)
        except SyntaxError as e:
            self.fail(f"05_trends.py contains syntax compilation errors: {e}")

    def test_sectors_page_syntax_and_compilation(self):
        """Validates that pages/06_sectors.py is free of syntax errors and compiles cleanly."""
        file_path = BASE_DIR / "pages" / "06_sectors.py"
        self.assertTrue(file_path.exists(), f"Missing target page file at: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
            
        try:
            compiled = compile(source_code, str(file_path), "exec")
            self.assertIsNotNone(compiled)
        except SyntaxError as e:
            self.fail(f"06_sectors.py contains syntax compilation errors: {e}")

    def test_capital_page_syntax_and_compilation(self):
        """Validates that pages/07_capital.py is free of syntax errors and compiles cleanly."""
        file_path = BASE_DIR / "pages" / "07_capital.py"
        self.assertTrue(file_path.exists(), f"Missing target page file at: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
            
        try:
            compiled = compile(source_code, str(file_path), "exec")
            self.assertIsNotNone(compiled)
        except SyntaxError as e:
            self.fail(f"07_capital.py contains syntax compilation errors: {e}")

    def test_reports_page_syntax_and_compilation(self):
        """Validates that pages/08_reports.py is free of syntax errors and compiles cleanly."""
        file_path = BASE_DIR / "pages" / "08_reports.py"
        self.assertTrue(file_path.exists(), f"Missing target page file at: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
            
        try:
            compiled = compile(source_code, str(file_path), "exec")
            self.assertIsNotNone(compiled)
        except SyntaxError as e:
            self.fail(f"08_reports.py contains syntax compilation errors: {e}")


if __name__ == "__main__":
    unittest.main()