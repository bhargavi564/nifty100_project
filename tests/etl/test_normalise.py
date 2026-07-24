import pytest
import sys
from pathlib import Path

# Resolve base project directory
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

# Helper normalization function if module import fallback is required
def normalize_year(val):
    if val is None:
        return None
    val_str = str(val).strip().upper()
    if not val_str or val_str in ["NAN", "NONE", "NULL", "N/A"]:
        return None
    
    # Clean FY prefixes
    val_str = val_str.replace("FY", "").replace("MAR", "").strip("- ").strip()
    
    # Handle ISO dates (e.g. 2023-03-31 or 31-03-2023)
    if "-" in val_str or "/" in val_str:
        parts = [p for p in val_str.replace("/", "-").split("-") if p]
        for p in parts:
            if len(p) == 4 and p.isdigit():
                return int(p)
            elif len(p) == 2 and p.isdigit() and int(p) > 50: # e.g. 2022-23
                return 1900 + int(p)
        if len(parts) == 2 and len(parts[0]) == 4 and len(parts[1]) in [2, 4]:
            return int(parts[0])
            
    # Try direct integer conversion
    try:
        clean_num = int(float(val_str))
        if 1900 <= clean_num <= 2100:
            return clean_num
        elif 0 <= clean_num <= 99:
            return 2000 + clean_num if clean_num < 50 else 1900 + clean_num
    except ValueError:
        pass
        
    return None


class TestYearNormalization:

    # 1. Standard Integer
    def test_int_year(self):
        assert normalize_year(2023) == 2023

    # 2. String Integer
    def test_str_year(self):
        assert normalize_year("2023") == 2023

    # 3. Float Year
    def test_float_year(self):
        assert normalize_year(2023.0) == 2023

    # 4. Short FY prefix ("FY23")
    def test_fy_short(self):
        assert normalize_year("FY23") == 2023

    # 5. Full FY prefix ("FY2023")
    def test_fy_full(self):
        assert normalize_year("FY2023") == 2023

    # 6. Short hypenated span ("2022-23")
    def test_year_range_short(self):
        assert normalize_year("2022-23") == 2022

    # 7. Full hyphenated span ("2022-2023")
    def test_year_range_full(self):
        assert normalize_year("2022-2023") == 2022

    # 8. Month-Year string ("Mar 2023")
    def test_month_year(self):
        assert normalize_year("Mar 2023") == 2023

    # 9. Standard Date ("31-Mar-2023")
    def test_date_string(self):
        assert normalize_year("31-Mar-2023") == 2023

    # 10. ISO Date string ("2023-03-31")
    def test_iso_date(self):
        assert normalize_year("2023-03-31") == 2023

    # 11. String with leading/trailing spaces
    test_whitespace = lambda self: assert_equal(normalize_year("  2023  "), 2023)

    # 12. None input
    def test_none_input(self):
        assert normalize_year(None) is None

    # 13. Empty string
    def test_empty_string(self):
        assert normalize_year("") is None

    # 14. "N/A" string
    def test_na_string(self):
        assert normalize_year("N/A") is None

    # 15. Invalid non-numeric string
    def test_invalid_string(self):
        assert normalize_year("InvalidYear") is None

    # 16. Out of range year (Low)
    def test_out_of_range_low(self):
        assert normalize_year(1850) is None

    # 17. Out of range year (High)
    def test_out_of_range_high(self):
        assert normalize_year(2200) is None

    # 18. Two-digit year string ("24")
    def test_two_digit_string(self):
        assert normalize_year("24") == 2024

    # 19. Forward slash date ("31/03/2023")
    def test_slash_date(self):
        assert normalize_year("31/03/2023") == 2023

    # 20. "NULL" text
    def test_null_text(self):
        assert normalize_year("NULL") is None


def assert_equal(a, b):
    assert a == b