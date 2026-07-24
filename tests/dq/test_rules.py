import pytest
import pandas as pd

# Mock rule validator engine
def validate_dq_rules(df):
    violations = []
    
    for idx, row in df.iterrows():
        comp = row.get("company_id", "UNKNOWN")
        
        # DQ-001: Missing Company ID (CRITICAL)
        if pd.isna(row.get("company_id")) or str(row.get("company_id")).strip() == "":
            violations.append({"rule_id": "DQ-001", "severity": "CRITICAL", "company_id": comp})
            
        # DQ-002: Invalid Year Format (HIGH)
        year = row.get("year")
        if pd.notna(year) and (not isinstance(year, int) or year < 2000 or year > 2030):
            violations.append({"rule_id": "DQ-002", "severity": "HIGH", "company_id": comp})

        # DQ-003: Negative Revenue (HIGH)
        if row.get("revenue", 0) < 0:
            violations.append({"rule_id": "DQ-003", "severity": "HIGH", "company_id": comp})

        # DQ-004: Negative Total Assets (CRITICAL)
        if row.get("total_assets", 0) < 0:
            violations.append({"rule_id": "DQ-004", "severity": "CRITICAL", "company_id": comp})

        # DQ-005: Balance Sheet Imbalance (Assets != Equity + Liabilities) (CRITICAL)
        assets = row.get("total_assets")
        eq_liab = row.get("total_equity_liabilities")
        if assets is not None and eq_liab is not None and abs(assets - eq_liab) > 1.0:
            violations.append({"rule_id": "DQ-005", "severity": "CRITICAL", "company_id": comp})

        # DQ-006: OPM > 100% (MEDIUM)
        if row.get("operating_profit_margin_pct", 0) > 100.0:
            violations.append({"rule_id": "DQ-006", "severity": "MEDIUM", "company_id": comp})

        # DQ-007: Net Margin > OPM (MEDIUM)
        opm = row.get("operating_profit_margin_pct")
        npm = row.get("net_profit_margin_pct")
        if opm is not None and npm is not None and npm > opm and opm > 0:
            violations.append({"rule_id": "DQ-007", "severity": "MEDIUM", "company_id": comp})

        # DQ-008: Debt to Equity > 20x (HIGH)
        if row.get("debt_to_equity", 0) > 20.0:
            violations.append({"rule_id": "DQ-008", "severity": "HIGH", "company_id": comp})

        # DQ-009: Tax Paid < 0 (LOW)
        if row.get("tax_paid", 0) < 0:
            violations.append({"rule_id": "DQ-009", "severity": "LOW", "company_id": comp})

        # DQ-010: Negative Market Capitalization (CRITICAL)
        if row.get("market_cap", 0) < 0:
            violations.append({"rule_id": "DQ-010", "severity": "CRITICAL", "company_id": comp})

        # DQ-011: Promoters Holding > 100% (HIGH)
        if row.get("promoter_holding_pct", 0) > 100.0:
            violations.append({"rule_id": "DQ-011", "severity": "HIGH", "company_id": comp})

        # DQ-012: Negative Depreciation (MEDIUM)
        if row.get("depreciation", 0) < 0:
            violations.append({"rule_id": "DQ-012", "severity": "MEDIUM", "company_id": comp})

        # DQ-013: Face Value <= 0 (LOW)
        if "face_value" in row and row["face_value"] <= 0:
            violations.append({"rule_id": "DQ-013", "severity": "LOW", "company_id": comp})

        # DQ-014: Duplicate Ticker-Year Record (HIGH)
        if row.get("is_duplicate", False):
            violations.append({"rule_id": "DQ-014", "severity": "HIGH", "company_id": comp})

    return violations


class TestDQRules:

    def test_dq_001_missing_company_id(self):
        df = pd.DataFrame([{"company_id": None, "year": 2023}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-001"
        assert res[0]["severity"] == "CRITICAL"

    def test_dq_002_invalid_year_format(self):
        df = pd.DataFrame([{"company_id": "TCS", "year": 1890}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-002"
        assert res[0]["severity"] == "HIGH"

    def test_dq_003_negative_revenue(self):
        df = pd.DataFrame([{"company_id": "TCS", "revenue": -100.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-003"
        assert res[0]["severity"] == "HIGH"

    def test_dq_004_negative_assets(self):
        df = pd.DataFrame([{"company_id": "TCS", "total_assets": -50.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-004"
        assert res[0]["severity"] == "CRITICAL"

    def test_dq_005_balance_sheet_imbalance(self):
        df = pd.DataFrame([{"company_id": "TCS", "total_assets": 1000.0, "total_equity_liabilities": 900.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-005"
        assert res[0]["severity"] == "CRITICAL"

    def test_dq_006_excessive_opm(self):
        df = pd.DataFrame([{"company_id": "TCS", "operating_profit_margin_pct": 120.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-006"
        assert res[0]["severity"] == "MEDIUM"

    def test_dq_007_npm_greater_than_opm(self):
        df = pd.DataFrame([{"company_id": "TCS", "operating_profit_margin_pct": 15.0, "net_profit_margin_pct": 25.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-007"
        assert res[0]["severity"] == "MEDIUM"

    def test_dq_008_excessive_debt_to_equity(self):
        df = pd.DataFrame([{"company_id": "TCS", "debt_to_equity": 25.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-008"
        assert res[0]["severity"] == "HIGH"

    def test_dq_009_negative_tax_paid(self):
        df = pd.DataFrame([{"company_id": "TCS", "tax_paid": -10.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-009"
        assert res[0]["severity"] == "LOW"

    def test_dq_010_negative_market_cap(self):
        df = pd.DataFrame([{"company_id": "TCS", "market_cap": -500.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-010"
        assert res[0]["severity"] == "CRITICAL"

    def test_dq_011_excessive_promoter_holding(self):
        df = pd.DataFrame([{"company_id": "TCS", "promoter_holding_pct": 105.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-011"
        assert res[0]["severity"] == "HIGH"

    def test_dq_012_negative_depreciation(self):
        df = pd.DataFrame([{"company_id": "TCS", "depreciation": -15.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-012"
        assert res[0]["severity"] == "MEDIUM"

    def test_dq_013_invalid_face_value(self):
        df = pd.DataFrame([{"company_id": "TCS", "face_value": 0.0}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-013"
        assert res[0]["severity"] == "LOW"

    def test_dq_014_duplicate_record(self):
        df = pd.DataFrame([{"company_id": "TCS", "is_duplicate": True}])
        res = validate_dq_rules(df)
        assert len(res) == 1
        assert res[0]["rule_id"] == "DQ-014"
        assert res[0]["severity"] == "HIGH"