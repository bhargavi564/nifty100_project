import pytest
import math

def calculate_roe(net_income, total_equity):
    if total_equity is None or total_equity <= 0:
        return None
    return (net_income / total_equity) * 100

def calculate_de(total_debt, total_equity):
    if total_equity is None or total_equity <= 0:
        return None
    if total_debt is None or total_debt == 0:
        return 0.0
    return total_debt / total_equity

def calculate_icr(ebit, interest_expense):
    if interest_expense is None or interest_expense == 0:
        return None
    return ebit / interest_expense

def calculate_cagr(start_val, end_val, periods=5):
    if start_val is None or end_val is None or periods <= 0:
        return None, None
    if start_val <= 0 and end_val > 0:
        return None, "TURNAROUND"
    if start_val > 0 and end_val <= 0:
        return None, "DECLINE_TO_LOSS"
    if start_val <= 0 and end_val <= 0:
        return None, "NEGATIVE_PERIOD"
    
    cagr = ((end_val / start_val) ** (1 / periods) - 1) * 100
    return round(cagr, 2), "NORMAL"

def flag_high_de_non_financial(de_ratio, is_financial=False):
    if not is_financial and de_ratio is not None and de_ratio > 5.0:
        return True
    return False

def flag_opm_divergence(reported_opm, calculated_opm, threshold=5.0):
    if reported_opm is None or calculated_opm is None:
        return False
    return abs(reported_opm - calculated_opm) > threshold

def calculate_cfo_quality_score(cfo, net_profit):
    if net_profit is None or net_profit == 0 or cfo is None:
        return 0.0
    ratio = cfo / net_profit
    if ratio >= 1.2: return 100.0
    elif ratio >= 1.0: return 80.0
    elif ratio >= 0.8: return 60.0
    elif ratio > 0: return 40.0
    else: return 0.0


class TestKPIRatios:

    # 1. ROE with Positive Equity
    def test_roe_positive_equity(self):
        assert calculate_roe(200, 1000) == 20.0

    # 2. ROE with Negative Equity (returns None)
    def test_roe_negative_equity(self):
        assert calculate_roe(200, -500) is None

    # 3. ROE with Zero Equity (returns None)
    def test_roe_zero_equity(self):
        assert calculate_roe(200, 0) is None

    # 4. D/E for Debt-Free Company (returns 0)
    def test_de_debt_free(self):
        assert calculate_de(0, 1000) == 0.0

    # 5. D/E Standard Calculation
    def test_de_standard(self):
        assert calculate_de(500, 1000) == 0.5

    # 6. D/E with Negative Equity
    def test_de_negative_equity(self):
        assert calculate_de(500, -100) is None

    # 7. ICR when Interest = 0 (returns None)
    def test_icr_zero_interest(self):
        assert calculate_icr(500, 0) is None

    # 8. ICR Standard Calculation
    def test_icr_standard(self):
        assert calculate_icr(500, 50) == 10.0

    # 9. D/E > 5 Flag for Non-Financial Company
    def test_high_de_non_financial_flag(self):
        assert flag_high_de_non_financial(6.2, is_financial=False) is True

    # 10. D/E > 5 Flag Ignored for Financial Company
    def test_high_de_financial_ignored(self):
        assert flag_high_de_non_financial(6.2, is_financial=True) is False

    # 11. Normal CAGR Calculation
    def test_cagr_normal(self):
        cagr, flag = calculate_cagr(100, 200, 5)
        assert cagr == 14.87
        assert flag == "NORMAL"

    # 12. CAGR Turnaround Flag (Loss to Profit)
    def test_cagr_turnaround(self):
        cagr, flag = calculate_cagr(-50, 100, 5)
        assert cagr is None
        assert flag == "TURNAROUND"

    # 13. CAGR Decline-to-Loss Flag (Profit to Loss)
    def test_cagr_decline_to_loss(self):
        cagr, flag = calculate_cagr(100, -50, 5)
        assert cagr is None
        assert flag == "DECLINE_TO_LOSS"

    # 14. CAGR Both Negative
    def test_cagr_both_negative(self):
        cagr, flag = calculate_cagr(-100, -50, 5)
        assert cagr is None
        assert flag == "NEGATIVE_PERIOD"

    # 15. OPM Cross-Check Divergence Flag (Divergence > Threshold)
    def test_opm_divergence_true(self):
        assert flag_opm_divergence(25.0, 18.0, threshold=5.0) is True

    # 16. OPM Cross-Check Divergence Flag (Divergence <= Threshold)
    def test_opm_divergence_false(self):
        assert flag_opm_divergence(22.0, 20.0, threshold=5.0) is False

    # 17. CFO Quality Score High Ratio
    def test_cfo_quality_score_high(self):
        assert calculate_cfo_quality_score(130, 100) == 100.0

    # 18. CFO Quality Score Good Ratio
    def test_cfo_quality_score_good(self):
        assert calculate_cfo_quality_score(105, 100) == 80.0

    # 19. CFO Quality Score Moderate Ratio
    def test_cfo_quality_score_moderate(self):
        assert calculate_cfo_quality_score(85, 100) == 60.0

    # 20. CFO Quality Score Negative Cash Flow
    def test_cfo_quality_score_negative(self):
        assert calculate_cfo_quality_score(-20, 100) == 0.0