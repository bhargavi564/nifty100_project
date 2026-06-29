def net_profit_margin(net_profit, sales):
              
    if sales == 0:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(op_profit, sales):

    if sales == 0:
        return None

    return (op_profit / sales) * 100


def roe(net_profit, equity, reserves):

    capital = equity + reserves

    if capital <= 0:
        return None

    return (net_profit / capital) * 100


def roce(ebit, equity, reserves, borrowings):

    capital = equity + reserves + borrowings

    if capital <= 0:
        return None

    return (ebit / capital) * 100


def roa(net_profit, assets):

    if assets == 0:
        return None

    return (net_profit / assets) * 100


def net_profit_margin(net_profit, sales):

    if sales == 0:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(op_profit, sales):

    if sales == 0:
        return None

    return (op_profit / sales) * 100


def roe(net_profit, equity, reserves):

    capital = equity + reserves

    if capital <= 0:
        return None

    return (net_profit / capital) * 100


def roce(ebit, equity, reserves, borrowings):

    capital = equity + reserves + borrowings

    if capital <= 0:
        return None

    return (ebit / capital) * 100


def roa(net_profit, assets):

    if assets == 0:
        return None

    return (net_profit / assets) * 100

if __name__ == "__main__":
              
    print("Net Profit Margin:", net_profit_margin(200, 1000))
    print("Operating Profit Margin:", operating_profit_margin(150, 1000))
    print("ROE:", roe(250, 1000, 500))
    print("ROCE:",roce(400,1000,200,300))
    print("ROA:",roa(500,5000))