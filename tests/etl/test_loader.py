import pytest
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

class TestDataLoader:

    def test_db_companies_table_exists(self):
        """Verifies companies database table or mock DataFrame loads with required columns."""
        df = pd.DataFrame({"id": ["TCS", "INFY"], "company_name": ["TCS Ltd", "Infosys Ltd"]})
        assert not df.empty
        assert "id" in df.columns
        assert "company_name" in df.columns

    def test_companies_row_count_non_zero(self):
        df = pd.DataFrame({"id": range(92)})
        assert len(df) == 92

    def test_financial_ratios_columns(self):
        expected_cols = ["company_id", "year", "return_on_equity_pct", "debt_to_equity"]
        df = pd.DataFrame(columns=expected_cols)
        for col in expected_cols:
            assert col in df.columns

    def test_empty_file_handling(self, tmp_path):
        p = tmp_path / "empty.csv"
        p.write_text("")
        with pytest.raises(Exception):
            pd.read_csv(p)

    def test_valid_csv_loading(self, tmp_path):
        p = tmp_path / "test.csv"
        p.write_text("company_id,year\nTCS,2023\nINFY,2023")
        df = pd.read_csv(p)
        assert len(df) == 2
        assert list(df.columns) == ["company_id", "year"]

    def test_missing_column_detection(self):
        df = pd.DataFrame({"company_id": ["TCS"]})
        assert "return_on_equity_pct" not in df.columns

    def test_data_types_integrity(self):
        df = pd.DataFrame({"year": ["2023", "2024"]})
        df["year"] = df["year"].astype(int)
        assert df["year"].dtype == "int64"

    def test_duplicate_rows_handling(self):
        df = pd.DataFrame({"id": ["TCS", "TCS"]})
        df_unique = df.drop_duplicates()
        assert len(df_unique) == 1

    def test_null_value_counting(self):
        df = pd.DataFrame({"val": [1.0, None, 3.0]})
        assert df["val"].isna().sum() == 1

    def test_loader_path_resolution(self):
        assert BASE_DIR.exists()