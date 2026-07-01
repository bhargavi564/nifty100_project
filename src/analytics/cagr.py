import math


# -----------------------------------
# Generic CAGR Function
# -----------------------------------
def calculate_cagr(start, end, years):

    if years <= 0:
        return None, "INVALID"

    if start == 0:
        return None, "ZERO_BASE"

    if start > 0 and end > 0:
        cagr = ((end / start) ** (1 / years) - 1) * 100
        return round(cagr, 2), "NORMAL"

    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"

    if start < 0 and end > 0:
        return None, "TURNAROUND"

    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"

    return None, "UNKNOWN"


# -----------------------------------
# Revenue CAGR
# -----------------------------------
def revenue_cagr(start_sales, end_sales, years):
    return calculate_cagr(start_sales, end_sales, years)


# -----------------------------------
# PAT CAGR
# -----------------------------------
def pat_cagr(start_pat, end_pat, years):
    return calculate_cagr(start_pat, end_pat, years)


# -----------------------------------
# EPS CAGR
# -----------------------------------
def eps_cagr(start_eps, end_eps, years):
    return calculate_cagr(start_eps, end_eps, years)


# -----------------------------------
# Check Required Years
# -----------------------------------
def check_years(total_years, required):

    if total_years < required:
        return None, "INSUFFICIENT"

    return True, "OK"


# -----------------------------------
# Demo Section
# -----------------------------------
if __name__ == "__main__":

    print("Revenue CAGR")

    print(revenue_cagr(100, 200, 3))
    print(revenue_cagr(100, 300, 5))
    print(revenue_cagr(100, 500, 10))

    print("\nPAT CAGR")

    print(pat_cagr(50, 120, 3))
    print(pat_cagr(60, 180, 5))
    print(pat_cagr(100, 400, 10))

    print("\nEPS CAGR")

    print(eps_cagr(10, 20, 3))
    print(eps_cagr(12, 36, 5))
    print(eps_cagr(15, 60, 10))

    print("\nEdge Cases")

    print(calculate_cagr(0, 100, 5))
    print(calculate_cagr(-100, 200, 5))
    print(calculate_cagr(100, -50, 5))
    print(calculate_cagr(-50, -20, 5))

    print("\nYear Check")

    print(check_years(2, 5))
    print(check_years(5, 5))