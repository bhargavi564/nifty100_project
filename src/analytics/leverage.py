def debt_to_equity(borrowings, equity, reserves):
              
    if borrowings == 0:
        return 0

    capital = equity + reserves

    if capital <= 0:
        return None

    return borrowings / capital


def high_leverage_flag(de_ratio, sector):

    if de_ratio is None:
        return False

    return de_ratio > 5 and sector.lower() != "financials"


def interest_coverage(op_profit, other_income, interest):

    if interest == 0:
        return None

    return (op_profit + other_income) / interest


def icr_label(icr):

    if icr is None:
        return "Debt Free"

    return "Has Debt"


def icr_warning(icr):

    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings, investments):

    return borrowings - investments


def asset_turnover(sales, assets):

    if assets == 0:
        return None

    return sales / assets


# -----------------------------
# Test Output
# -----------------------------
if __name__ == "__main__":

    de = debt_to_equity(500, 1000, 500)
    print("Debt to Equity:", de)

    flag = high_leverage_flag(de, "IT")
    print("High Leverage Flag:", flag)

    icr = interest_coverage(300, 50, 100)
    print("Interest Coverage Ratio:", icr)

    print("ICR Label:", icr_label(icr))

    print("ICR Warning:", icr_warning(icr))

    print("Net Debt:", net_debt(1000, 250))

    print("Asset Turnover:", asset_turnover(5000, 2500))