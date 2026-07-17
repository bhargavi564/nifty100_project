import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "pages"))


class TestDay23FrontEndRouting(unittest.TestCase):

    def test_home_page_module_syntax_parsable(self):
        """Validates that pages/01_home.py compiles safely."""
        home_path = BASE_DIR / "pages" / "01_home.py"
        self.assertTrue(home_path.exists())
        
        with open(home_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        try:
            compiled = compile(source, str(home_path), "exec")
            self.assertIsNotNone(compiled)
        except SyntaxError as e:
            self.fail(f"Home module contains parsing syntax errors: {e}")

    def test_profile_page_module_syntax_parsable(self):
        """Validates that pages/02_profile.py compiles safely."""
        profile_path = BASE_DIR / "pages" / "02_profile.py"
        self.assertTrue(profile_path.exists())
        
        with open(profile_path, "r", encoding="utf-8") as f:
            source = f.read()
            
        try:
            compiled = compile(source, str(profile_path), "exec")
            self.assertIsNotNone(compiled)
        except SyntaxError as e:
            self.fail(f"Profile module contains parsing syntax errors: {e}")


if __name__ == "__main__":
    unittest.main()